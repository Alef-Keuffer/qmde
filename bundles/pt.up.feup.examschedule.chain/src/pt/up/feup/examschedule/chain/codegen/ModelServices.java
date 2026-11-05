package pt.up.feup.examschedule.chain.codegen;

import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.resource.Resource;

import pt.up.feup.examschedule.conflictgraph.ConflictGraph;
import pt.up.feup.examschedule.solverconfig.SolverConfig;

/** Acceleo services: reach the sibling models of the same problem (they share one resource set). */
public class ModelServices {

	public SolverConfig solverConfig(EObject context) {
		return sibling(context, SolverConfig.class);
	}

	public ConflictGraph conflictGraph(EObject context) {
		return sibling(context, ConflictGraph.class);
	}

	private static <T> T sibling(EObject context, Class<T> type) {
		for (Resource resource : context.eResource().getResourceSet().getResources()) {
			for (EObject root : resource.getContents()) {
				if (type.isInstance(root)) {
					return type.cast(root);
				}
			}
		}
		throw new IllegalStateException("No " + type.getSimpleName() + " next to " + context.eResource().getURI());
	}
}
