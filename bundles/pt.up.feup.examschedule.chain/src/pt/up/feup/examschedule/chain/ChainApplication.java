package pt.up.feup.examschedule.chain;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.util.EcoreUtil;
import org.eclipse.equinox.app.IApplication;
import org.eclipse.equinox.app.IApplicationContext;

import pt.up.feup.examschedule.conflictgraph.ConflictGraphPackage;
import pt.up.feup.examschedule.dsl.ExamStandaloneSetup;
import pt.up.feup.examschedule.hamiltonian.HamiltonianPackage;
import pt.up.feup.examschedule.ising.IsingPackage;
import pt.up.feup.examschedule.problem.Problem;
import pt.up.feup.examschedule.problem.ProblemPackage;
import pt.up.feup.examschedule.qubo.QuboPackage;
import pt.up.feup.examschedule.solverconfig.SolverConfig;
import pt.up.feup.examschedule.solverconfig.SolverConfigFactory;
import pt.up.feup.examschedule.solverconfig.SolverConfigPackage;

/**
 * Headless entry point: runs the whole model chain for one problem, or for every {@code .exam} file in a
 * folder, writing each intermediate model and the generated script to {@code <outRoot>/<problem name>/}.
 * <p>
 * Usage: {@code -application pt.up.feup.examschedule.chain.run <file.exam|file.xmi|folder> <outRoot>}
 */
public class ChainApplication implements IApplication {

	private static final String CODEGEN_MODULE = "pt::up::feup::examschedule::chain::codegen::main";

	@Override
	public Object start(IApplicationContext context) throws Exception {
		String[] args = (String[]) context.getArguments().get(IApplicationContext.APPLICATION_ARGS);
		if (args.length != 2) {
			System.err.println("Usage: <file.exam|file.xmi|folder> <outRoot>");
			return 1;
		}
		ExamStandaloneSetup.doSetup();
		File outRoot = new File(args[1]).getAbsoluteFile();
		boolean ok = true;
		for (File input : inputs(new File(args[0]).getAbsoluteFile())) {
			System.out.println("== " + input.getName());
			ok &= run(input, outRoot);
		}
		return ok ? IApplication.EXIT_OK : 1;
	}

	private static List<File> inputs(File input) {
		if (!input.isDirectory()) {
			return List.of(input);
		}
		File[] files = input.listFiles((dir, name) -> name.endsWith(".exam"));
		List<File> sorted = new ArrayList<>(Arrays.asList(files == null ? new File[0] : files));
		sorted.sort(null);
		return sorted;
	}

	private static boolean run(File input, File outRoot) throws IOException {
		ResourceSet resourceSet = new ResourceSetImpl();
		Resource source = resourceSet.getResource(URI.createFileURI(input.getPath()), true);
		if (!source.getErrors().isEmpty()) {
			source.getErrors().forEach(error -> System.err.println(
					input.getName() + ":" + error.getLine() + ": " + error.getMessage()));
			return false;
		}
		if (!Validation.isValid(source)) {
			return false;
		}
		Problem problemRoot = EcoreUtil.copy(find(source, Problem.class));
		SolverConfig configRoot = find(source, SolverConfig.class);
		configRoot = configRoot == null ? SolverConfigFactory.eINSTANCE.createSolverConfig() : EcoreUtil.copy(configRoot);

		File outDir = new File(outRoot, problemRoot.getName());
		outDir.mkdirs();
		Resource problem = save(resourceSet, outDir, "problem.xmi", problemRoot);
		Resource config = save(resourceSet, outDir, "solverconfig.xmi", configRoot);

		Resource conflictGraph = model(resourceSet, outDir, "conflictgraph.xmi");
		Atl.transform("problem2conflictgraph",
				Map.of("Problem", ProblemPackage.eNS_URI, "ConflictGraph", ConflictGraphPackage.eNS_URI),
				Map.of("IN", problem), Map.of("OUT", conflictGraph));
		Resource hamiltonian = model(resourceSet, outDir, "hamiltonian.xmi");
		Atl.transform("conflictgraph2hamiltonian",
				Map.of("ConflictGraph", ConflictGraphPackage.eNS_URI, "SolverConfig", SolverConfigPackage.eNS_URI,
						"Hamiltonian", HamiltonianPackage.eNS_URI),
				Map.of("IN", conflictGraph, "CFG", config), Map.of("OUT", hamiltonian));
		Resource qubo = model(resourceSet, outDir, "qubo.xmi");
		Atl.transform("hamiltonian2qubo",
				Map.of("Hamiltonian", HamiltonianPackage.eNS_URI, "QUBO", QuboPackage.eNS_URI),
				Map.of("IN", hamiltonian), Map.of("OUT", qubo));
		Resource ising = model(resourceSet, outDir, "ising.xmi");
		Atl.transform("qubo2ising",
				Map.of("QUBO", QuboPackage.eNS_URI, "Ising", IsingPackage.eNS_URI),
				Map.of("IN", qubo), Map.of("OUT", ising));

		for (Resource resource : List.of(conflictGraph, hamiltonian, qubo, ising)) {
			resource.save(null);
			if (!Validation.isValid(resource)) {
				return false;
			}
		}
		Acceleo.generate(CODEGEN_MODULE, ising, outDir);
		return true;
	}

	private static <T> T find(Resource resource, Class<T> type) {
		for (var it = resource.getAllContents(); it.hasNext();) {
			EObject next = it.next();
			if (type.isInstance(next)) {
				return type.cast(next);
			}
		}
		return null;
	}

	private static Resource model(ResourceSet resourceSet, File outDir, String fileName) {
		return resourceSet.createResource(URI.createFileURI(new File(outDir, fileName).getPath()));
	}

	private static Resource save(ResourceSet resourceSet, File outDir, String fileName, EObject root)
			throws IOException {
		Resource resource = model(resourceSet, outDir, fileName);
		resource.getContents().add(root);
		resource.save(null);
		return resource;
	}

	@Override
	public void stop() {
	}
}
