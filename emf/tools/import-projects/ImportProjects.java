package pt.up.feup.examschedule.tools;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Stream;

import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IProjectDescription;
import org.eclipse.core.resources.IWorkspace;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.equinox.app.IApplication;
import org.eclipse.equinox.app.IApplicationContext;

/**
 * Headless File → Import → Existing Projects: imports every project under a folder, nested ones
 * included and none copied, into the workspace given with -data, then saves it.
 * Usage: eclipse -application pt.up.feup.examschedule.tools.importProjects -data ws folder
 */
public class ImportProjects implements IApplication {

	@Override
	public Object start(IApplicationContext context) throws Exception {
		String[] args = (String[]) context.getArguments().get(IApplicationContext.APPLICATION_ARGS);
		IWorkspace workspace = ResourcesPlugin.getWorkspace();
		List<Path> projectFiles;
		try (Stream<Path> files = Files.walk(Path.of(args[0]).toAbsolutePath())) {
			projectFiles = files.filter(f -> f.getFileName().toString().equals(".project")).toList();
		}
		for (Path projectFile : projectFiles) {
			IProjectDescription description = workspace.loadProjectDescription(IPath.fromPath(projectFile));
			description.setLocation(IPath.fromPath(projectFile.getParent()));
			IProject project = workspace.getRoot().getProject(description.getName());
			project.create(description, null);
			project.open(null);
			System.out.println("imported " + project.getName() + " from " + projectFile.getParent());
		}
		// Let the import's follow-up jobs (m2e's project registry, Xtext, PDE) finish before saving.
		while (!Job.getJobManager().isIdle()) {
			Thread.sleep(200);
		}
		workspace.save(true, null);
		// No project means a wrong folder, and an empty workspace would look clean.
		return projectFiles.isEmpty() ? 1 : EXIT_OK;
	}

	@Override
	public void stop() {
	}
}
