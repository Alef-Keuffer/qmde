package pt.up.feup.examschedule.chain;

import java.io.File;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.acceleo.Module;
import org.eclipse.acceleo.Template;
import org.eclipse.acceleo.aql.AcceleoUtil;
import org.eclipse.acceleo.aql.evaluation.AcceleoEvaluator;
import org.eclipse.acceleo.aql.evaluation.strategy.DefaultGenerationStrategy;
import org.eclipse.acceleo.aql.evaluation.strategy.DefaultWriterFactory;
import org.eclipse.acceleo.aql.evaluation.strategy.IAcceleoGenerationStrategy;
import org.eclipse.acceleo.aql.parser.AcceleoParser;
import org.eclipse.acceleo.aql.parser.ModuleLoader;
import org.eclipse.acceleo.aql.validation.AcceleoValidator;
import org.eclipse.acceleo.query.AQLUtils;
import org.eclipse.acceleo.query.ast.TypeLiteral;
import org.eclipse.acceleo.query.runtime.impl.namespace.ClassLoaderQualifiedNameResolver;
import org.eclipse.acceleo.query.runtime.IValidationMessage;
import org.eclipse.acceleo.query.runtime.ValidationMessageLevel;
import org.eclipse.acceleo.query.runtime.impl.namespace.JavaLoader;
import org.eclipse.acceleo.query.runtime.namespace.IQualifiedNameQueryEnvironment;
import org.eclipse.acceleo.query.runtime.namespace.IQualifiedNameResolver;
import org.eclipse.emf.common.util.BasicMonitor;
import org.eclipse.emf.common.util.Diagnostic;
import org.eclipse.emf.common.util.Monitor;
import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;

/**
 * Runs an Acceleo 4 module from this bundle's classpath, following the standalone launcher in
 * Acceleo's {@code examples/MavenLauncher}.
 */
final class Acceleo {

	private Acceleo() {
	}

	static void generate(String moduleQualifiedName, Resource model, File outDir) {
		Monitor monitor = new BasicMonitor();
		URI targetUri = URI.createFileURI(outDir.getPath() + File.separator);
		Map<String, String> options = new LinkedHashMap<>();
		options.put(AcceleoUtil.NEW_LINE_OPTION, "\n");

		ResourceSet resourceSet = model.getResourceSet();
		IQualifiedNameResolver resolver = new ClassLoaderQualifiedNameResolver(Acceleo.class.getClassLoader(),
				EPackage.Registry.INSTANCE, AcceleoParser.QUALIFIER_SEPARATOR);
		IQualifiedNameQueryEnvironment queryEnvironment = AcceleoUtil.newAcceleoQueryEnvironment(options, resolver,
				resourceSet, false);
		AcceleoEvaluator evaluator = new AcceleoEvaluator(queryEnvironment.getLookupEngine(), "\n");
		resolver.addLoader(new ModuleLoader(new AcceleoParser(), evaluator));
		resolver.addLoader(new JavaLoader(AcceleoParser.QUALIFIER_SEPARATOR, false));
		IAcceleoGenerationStrategy strategy = new DefaultGenerationStrategy(resourceSet.getURIConverter(),
				new DefaultWriterFactory());

		Module module = (Module) resolver.resolve(moduleQualifiedName);
		if (module == null) {
			throw new IllegalStateException("Acceleo module not found: " + moduleQualifiedName);
		}
		AQLUtils.registerEPackages(queryEnvironment, EPackage.Registry.INSTANCE,
				AQLUtils.getAllNeededEPackages(resolver, moduleQualifiedName));
		List<String> errors = new ArrayList<>();
		for (IValidationMessage message : new AcceleoValidator(queryEnvironment)
				.validate(module.getAst(), moduleQualifiedName).getValidationMessages()) {
			if (message.getLevel() == ValidationMessageLevel.ERROR) {
				errors.add("at offset " + message.getStartPosition() + ": " + message.getMessage());
			}
		}
		if (!errors.isEmpty()) {
			throw new IllegalStateException("Invalid Acceleo module " + moduleQualifiedName + ": " + errors);
		}

		Map<EClass, List<EObject>> valuesCache = new LinkedHashMap<>();
		try {
			for (Template template : AcceleoUtil.getMainTemplates(module)) {
				TypeLiteral type = (TypeLiteral) template.getParameters().get(0).getType().getAst();
				String parameter = template.getParameters().get(0).getName();
				for (EObject value : AcceleoUtil.getValues(type, queryEnvironment, List.of(model), valuesCache,
						monitor)) {
					Map<String, Object> variables = new LinkedHashMap<>();
					variables.put(parameter, value);
					AcceleoUtil.generate(template, variables, evaluator, queryEnvironment, strategy, targetUri, null,
							monitor);
				}
			}
		} finally {
			AcceleoUtil.cleanServices(queryEnvironment, resourceSet);
		}

		Diagnostic diagnostic = evaluator.getGenerationResult().getDiagnostic();
		if (diagnostic.getSeverity() >= Diagnostic.ERROR) {
			List<String> messages = new ArrayList<>();
			diagnostic.getChildren().forEach(child -> messages.add(child.getMessage()));
			throw new IllegalStateException("Acceleo generation failed: " + messages);
		}
		evaluator.getGenerationResult().getGeneratedFiles()
				.forEach(file -> System.out.println("Generated " + file.toFileString()));
	}
}
