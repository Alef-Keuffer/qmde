package pt.up.feup.examschedule.chain;

import org.eclipse.emf.common.util.Diagnostic;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.util.Diagnostician;
import org.eclipse.ocl.xtext.essentialocl.EssentialOCLStandaloneSetup;

/** Checks a model against its metamodel's multiplicities and embedded OCL constraints. */
final class Validation {

	static {
		// The OCL expression parser is otherwise only registered by OCL's UI bundles.
		EssentialOCLStandaloneSetup.doSetup();
	}

	private Validation() {
	}

	static boolean isValid(Resource resource) {
		boolean valid = true;
		for (EObject root : resource.getContents()) {
			Diagnostic diagnostic = Diagnostician.INSTANCE.validate(root);
			if (diagnostic.getSeverity() >= Diagnostic.ERROR) {
				valid = false;
				System.err.println("Invalid model " + resource.getURI() + ":");
				for (Diagnostic child : diagnostic.getChildren()) {
					System.err.println("  " + child.getMessage());
					for (Throwable cause = child.getException(); cause != null; cause = cause.getCause()) {
						System.err.println("    caused by " + cause);
					}
				}
			}
		}
		return valid;
	}
}
