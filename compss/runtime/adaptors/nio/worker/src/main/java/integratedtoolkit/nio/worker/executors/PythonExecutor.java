package integratedtoolkit.nio.worker.executors;

import integratedtoolkit.nio.NIOTask;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;


public class PythonExecutor extends ExternalExecutor {
	
	private static final String PYCOMPSS_RELATIVE_PATH = File.separator + "Bindings" + File.separator + "python";
	private static final String EXTRAE_RELATIVE_PATH = File.separator + "Dependencies" + File.separator + "extrae";
	
	private static final String WORKER_PY_RELATIVE_PATH = File.separator + "pycompss" + File.separator + "worker" + File.separator + "worker.py";
	
	private static final String LIBEXEC_EXTRAE_RELATIVE_PATH = EXTRAE_RELATIVE_PATH + File.separator + "libexec";
	private static final String LIB_EXTRAE_RELATIVE_PATH = EXTRAE_RELATIVE_PATH + File.separator + "lib";
	
	private static final String WORKER_TRACING_CONFIG_FILE_RELATIVE_PATH = File.separator + "Runtime" + File.separator + "configuration" +
            File.separator + "xml" + File.separator + "tracing";

	@Override
	public ArrayList<String> getLaunchCommand(NIOTask nt, String sandBox) {
		ArrayList<String> lArgs = new ArrayList<String>();
		String pycompssHome = nt.getInstallDir() + PYCOMPSS_RELATIVE_PATH;

		if (tracing){
			int taskId = nt.getTaskId();
			String baseConfigFile = nt.getInstallDir() + WORKER_TRACING_CONFIG_FILE_RELATIVE_PATH + File.separator + "extrae_task.xml";
			String taskConfigFile = sandBox + File.separator + "task" + taskId + ".xml";
			lArgs.add("echo $(sed s/{{NAME}}/task" + taskId + "/g <<< $(cat " + baseConfigFile +")) > " + taskConfigFile + ";");
			lArgs.add("export EXTRAE_CONFIG_FILE=" + taskConfigFile + ";");
		}
		
		lArgs.add("python");
		lArgs.add("-u");
		lArgs.add(pycompssHome + WORKER_PY_RELATIVE_PATH);
		
		return lArgs;
	}

	@Override
	public Map<String, String> getEnvironment(NIOTask nt) {
		// PyCOMPSs HOME
		Map<String, String> env = new HashMap<String, String>();
		String pycompssHome = nt.getInstallDir() + PYCOMPSS_RELATIVE_PATH;
		env.put("PYCOMPSS_HOME", pycompssHome);
		
		// PYTHONPATH
		String pythonPath = System.getenv("PYTHONPATH");
		if (pythonPath == null) {
			pythonPath = pycompssHome + ":" + nt.getPythonPath() + ":" + nt.getAppDir();
		} else {
			pythonPath = pycompssHome + ":" + nt.getPythonPath() + ":" + nt.getAppDir() + pythonPath;
		}

        // ADD PYEXTRAE IF TRACING
        if (tracing){
            String libexec_extrae_path = nt.getInstallDir() + LIBEXEC_EXTRAE_RELATIVE_PATH;
            String lib_extrae_path = nt.getInstallDir() + LIB_EXTRAE_RELATIVE_PATH;
            pythonPath += ":" + libexec_extrae_path + ":" + lib_extrae_path ;
        }
		env.put("PYTHONPATH", pythonPath);
		
		// LD_LIBRARY_PATH
		String ldLibraryPath = System.getenv("LD_LIBRARY_PATH");
		if (ldLibraryPath == null) {
			ldLibraryPath = nt.getLibPath();
		} else {
			ldLibraryPath = ldLibraryPath.concat(":" + nt.getLibPath());
		}
		env.put("LD_LIBRARY_PATH", ldLibraryPath);
               
		return env;
	}

}
