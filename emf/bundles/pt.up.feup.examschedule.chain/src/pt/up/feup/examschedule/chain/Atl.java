package pt.up.feup.examschedule.chain;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.m2m.atl.emftvm.EmftvmFactory;
import org.eclipse.m2m.atl.emftvm.ExecEnv;
import org.eclipse.m2m.atl.emftvm.Metamodel;
import org.eclipse.m2m.atl.emftvm.Model;
import org.eclipse.m2m.atl.emftvm.Module;
import org.eclipse.m2m.atl.emftvm.compiler.AtlToEmftvmCompiler;
import org.eclipse.m2m.atl.emftvm.util.DefaultModuleResolver;
import org.eclipse.m2m.atl.emftvm.util.ModuleNotFoundException;
import org.eclipse.m2m.atl.emftvm.util.ModuleResolver;
import org.eclipse.m2m.atl.emftvm.util.TimingData;

/** Runs ATL transformations shipped in this bundle's {@code transforms/} folder on EMFTVM. */
final class Atl {

	private static final String TRANSFORMS = "platform:/plugin/pt.up.feup.examschedule.chain/transforms/";

	private Atl() {
	}

	/**
	 * @param metamodels ATL metamodel name to nsURI
	 * @param inputs     ATL model name to input resource
	 * @param outputs    ATL model name to (empty) output resource
	 */
	static void transform(String module, Map<String, String> metamodels, Map<String, Resource> inputs,
			Map<String, Resource> outputs) {
		EmftvmFactory factory = EmftvmFactory.eINSTANCE;
		ExecEnv env = factory.createExecEnv();
		metamodels.forEach((name, nsUri) -> {
			Metamodel metamodel = factory.createMetamodel();
			metamodel.setResource(EPackage.Registry.INSTANCE.getEPackage(nsUri).eResource());
			env.registerMetaModel(name, metamodel);
		});
		inputs.forEach((name, resource) -> env.registerInputModel(name, model(factory, resource)));
		outputs.forEach((name, resource) -> env.registerOutputModel(name, model(factory, resource)));
		env.loadModule(new AtlSourceResolver(), module);
		env.run(new TimingData());
	}

	private static Model model(EmftvmFactory factory, Resource resource) {
		Model model = factory.createModel();
		model.setResource(resource);
		return model;
	}

	/** Resolves modules by compiling this bundle's {@code .atl} sources to EMFTVM bytecode in memory. */
	private static final class AtlSourceResolver implements ModuleResolver {

		private final ResourceSet resourceSet = new ResourceSetImpl();

		@Override
		public Module resolveModule(String name) throws ModuleNotFoundException {
			String path = TRANSFORMS + name.replace("::", "/");
			ByteArrayOutputStream bytecode = new ByteArrayOutputStream();
			try (InputStream source = resourceSet.getURIConverter().createInputStream(URI.createURI(path + ".atl"))) {
				EObject[] problems = new AtlToEmftvmCompiler().compileWithProblemModel(source, bytecode);
				List<String> errors = new ArrayList<>();
				for (EObject problem : problems) {
					if ("error".equals(String.valueOf(get(problem, "severity")))) {
						errors.add(get(problem, "location") + ": " + get(problem, "description"));
					}
				}
				if (!errors.isEmpty()) {
					throw new ModuleNotFoundException("ATL compile errors in " + name + ": " + errors);
				}
				Resource resource = resourceSet.createResource(URI.createURI(path + DefaultModuleResolver.FILE_EXT));
				resource.load(new ByteArrayInputStream(bytecode.toByteArray()), null);
				return (Module) resource.getContents().get(0);
			} catch (IOException e) {
				throw new ModuleNotFoundException("Cannot compile ATL module " + path, e);
			}
		}

		private static Object get(EObject object, String feature) {
			return object.eGet(object.eClass().getEStructuralFeature(feature));
		}
	}
}
