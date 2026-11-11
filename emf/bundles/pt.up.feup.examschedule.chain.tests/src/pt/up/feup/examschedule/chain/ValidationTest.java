package pt.up.feup.examschedule.chain;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;

import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.impl.ResourceImpl;
import org.eclipse.emf.ecore.util.EcoreUtil;
import org.junit.jupiter.api.Test;

import pt.up.feup.examschedule.problem.Exam;
import pt.up.feup.examschedule.problem.Problem;
import pt.up.feup.examschedule.problem.ProblemFactory;
import pt.up.feup.examschedule.problem.Student;

class ValidationTest {

	@Test
	void acceptsOneStudentSittingOneExam() {
		Problem problem = problem();
		assertTrue(Validation.isValid(resource(problem)));
	}

	@Test
	void rejectsProblemWithoutExams() {
		Problem problem = problem();
		problem.getExams().clear();
		assertTooFew(problem, "exams");
	}

	@Test
	void rejectsProblemWithoutStudents() {
		Problem problem = problem();
		problem.getStudents().clear();
		problem.getExams().get(0).getStudents().clear();
		assertTooFew(problem, "students");
	}

	private static Problem problem() {
		ProblemFactory factory = ProblemFactory.eINSTANCE;
		Student student = factory.createStudent();
		student.setName("s");
		Exam exam = factory.createExam();
		exam.setName("e");
		exam.getStudents().add(student);
		Problem problem = factory.createProblem();
		problem.setName("p");
		problem.setNBatches(1);
		problem.getStudents().add(student);
		problem.getExams().add(exam);
		return problem;
	}

	private static void assertTooFew(Problem problem, String feature) {
		String errors = assertRejected(problem);
		assertTrue(errors.contains("The feature '" + feature + "' of '" + EcoreUtil.getIdentification(problem)
				+ "' with 0 values must have at least 1 values"), errors);
	}

	/** Checks that the validation step rejects the problem; returns what it printed. */
	private static String assertRejected(Problem problem) {
		Resource resource = resource(problem);
		ByteArrayOutputStream out = new ByteArrayOutputStream();
		PrintStream err = System.err;
		System.setErr(new PrintStream(out, true, StandardCharsets.UTF_8));
		try {
			assertFalse(Validation.isValid(resource), "accepted");
		} finally {
			System.setErr(err);
		}
		return out.toString(StandardCharsets.UTF_8);
	}

	private static Resource resource(Problem problem) {
		Resource resource = new ResourceImpl(URI.createURI("problem.xmi"));
		resource.getContents().add(problem);
		return resource;
	}
}
