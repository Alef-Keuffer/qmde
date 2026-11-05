package pt.up.feup.examschedule.chain;

import java.io.File;
import java.util.Map;

import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.equinox.app.IApplication;
import org.eclipse.equinox.app.IApplicationContext;

import pt.up.feup.examschedule.dsl.ExamStandaloneSetup;

/**
 * Headless entry point: runs the whole model chain for one problem instance.
 * <p>
 * Usage: {@code -application pt.up.feup.examschedule.chain.run <problem.exam|problem.xmi> <outDir>}
 */
public class ChainApplication implements IApplication {

	private static final String CONFLICT_GRAPH_NS = "https://pt/up/feup/examschedule/conflictgraph";

	@Override
	public Object start(IApplicationContext context) throws Exception {
		String[] args = (String[]) context.getArguments().get(IApplicationContext.APPLICATION_ARGS);
		if (args.length != 2) {
			System.err.println("Usage: <problem.exam|problem.xmi> <outDir>");
			return 1;
		}
		File problemFile = new File(args[0]).getAbsoluteFile();
		File outDir = new File(args[1]).getAbsoluteFile();
		outDir.mkdirs();

		ExamStandaloneSetup.doSetup();
		ResourceSet resourceSet = new ResourceSetImpl();
		Resource problem = resourceSet.getResource(URI.createFileURI(problemFile.getPath()), true);
		if (!problem.getErrors().isEmpty()) {
			problem.getErrors().forEach(error -> System.err.println(
					problemFile.getName() + ":" + error.getLine() + ": " + error.getMessage()));
			return 1;
		}
		if (!Validation.isValid(problem)) {
			return 1;
		}
		if (!problemFile.getName().endsWith(".xmi")) {
			Resource problemXmi = resourceSet.createResource(URI.createFileURI(new File(outDir, "problem.xmi").getPath()));
			problemXmi.getContents().addAll(problem.getContents());
			problemXmi.save(null);
			problem = problemXmi;
		}

		Resource conflictGraph = resourceSet.createResource(URI.createFileURI(new File(outDir, "conflictgraph.xmi").getPath()));
		Atl.transform("problem2conflictgraph",
				Map.of("Problem", problem.getContents().get(0).eClass().getEPackage().getNsURI(),
						"ConflictGraph", CONFLICT_GRAPH_NS),
				Map.of("IN", problem), Map.of("OUT", conflictGraph));
		conflictGraph.save(null);
		if (!Validation.isValid(conflictGraph)) {
			return 1;
		}

		Acceleo.generate("pt::up::feup::examschedule::chain::codegen::main", conflictGraph, outDir);
		return IApplication.EXIT_OK;
	}

	@Override
	public void stop() {
	}
}
