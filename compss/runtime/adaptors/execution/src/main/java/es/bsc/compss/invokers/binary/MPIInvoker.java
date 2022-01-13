/*
 *  Copyright 2002-2021 Barcelona Supercomputing Center (www.bsc.es)
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 */
package es.bsc.compss.invokers.binary;

import es.bsc.compss.COMPSsConstants;
import es.bsc.compss.exceptions.InvokeExecutionException;
import es.bsc.compss.exceptions.StreamCloseException;
import es.bsc.compss.execution.types.InvocationResources;
import es.bsc.compss.invokers.Invoker;
import es.bsc.compss.invokers.types.PythonParams;
import es.bsc.compss.invokers.types.StdIOStream;
import es.bsc.compss.invokers.util.BinaryRunner;
import es.bsc.compss.types.annotations.parameter.DataType;
import es.bsc.compss.types.execution.Invocation;
import es.bsc.compss.types.execution.InvocationContext;
import es.bsc.compss.types.execution.InvocationParam;
import es.bsc.compss.types.execution.LanguageParams;
import es.bsc.compss.types.execution.exceptions.JobExecutionException;
import es.bsc.compss.types.implementations.definition.MPIDefinition;

import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.util.ArrayList;


public class MPIInvoker extends Invoker {

    private static final int NUM_BASE_MPI_ARGS = 6;

    private static final String ERROR_TARGET_PARAM = "ERROR: MPI Execution doesn't support target parameters";

    MPIDefinition mpiDef;

    private BinaryRunner br;


    /**
     * MPI Invoker constructor.
     * 
     * @param context Task execution context.
     * @param invocation Task execution description.
     * @param taskSandboxWorkingDir Task execution sandbox directory.
     * @param assignedResources Assigned resources.
     * @throws JobExecutionException Error creating the MPI invoker.
     */
    public MPIInvoker(InvocationContext context, Invocation invocation, File taskSandboxWorkingDir,
        InvocationResources assignedResources) throws JobExecutionException {

        super(context, invocation, taskSandboxWorkingDir, assignedResources);

        // Get method definition properties
        try {
            this.mpiDef = (MPIDefinition) this.invocation.getMethodImplementation().getDefinition();
            this.mpiDef.setRunnerProperties(context.getInstallDir());
        } catch (Exception e) {
            throw new JobExecutionException(
                ERROR_METHOD_DEFINITION + this.invocation.getMethodImplementation().getMethodType(), e);
        }

        // Internal binary runner
        this.br = null;
    }

    private void checkArguments() throws JobExecutionException {
        try {
            mpiDef.checkArguments();
        } catch (IllegalArgumentException e) {
            throw new JobExecutionException(e);
        }
        if (this.invocation.getTarget() != null && this.invocation.getTarget().getValue() != null) {
            throw new JobExecutionException(ERROR_TARGET_PARAM);
        }
    }

    @Override
    public void invokeMethod() throws JobExecutionException {
        checkArguments();

        LOGGER.info("Invoked MPI " + this.mpiDef.getBinary() + " in " + this.context.getHostName());

        // Execute binary
        Object retValue;
        try {
            retValue = runInvocation();
        } catch (InvokeExecutionException iee) {
            throw new JobExecutionException(iee);
        }

        // Close out streams if any
        try {
            if (this.br != null) {
                // Python interpreter for direct access on stream property calls
                String pythonInterpreter = null;
                LanguageParams lp = this.context.getLanguageParams(COMPSsConstants.Lang.PYTHON);
                if (lp instanceof PythonParams) {
                    PythonParams pp = (PythonParams) lp;
                    pythonInterpreter = pp.getPythonInterpreter();
                }
                this.br.closeStreams(this.invocation.getParams(), pythonInterpreter);
            }
        } catch (StreamCloseException se) {
            LOGGER.error("Exception closing binary streams", se);
            throw new JobExecutionException(se);
        }

        // Update binary results
        for (InvocationParam np : this.invocation.getResults()) {
            if (np.getType() == DataType.FILE_T) {
                serializeBinaryExitValue(np, retValue);
            } else {
                np.setValue(retValue);
                np.setValueClass(retValue.getClass());
            }
        }
    }

    private Object runInvocation() throws InvokeExecutionException {
        // Command similar to
        // mpirun -H COMPSsWorker01,COMPSsWorker02 -n 2 (--bind-to core) exec args

        // Python interpreter for direct access on stream property calls
        String pythonInterpreter = null;
        LanguageParams lp = this.context.getLanguageParams(COMPSsConstants.Lang.PYTHON);
        if (lp instanceof PythonParams) {
            PythonParams pp = (PythonParams) lp;
            pythonInterpreter = pp.checkCoverageAndGetPythonInterpreter();

        }

        String[] appParams = new String[0];
        if (this.mpiDef.hasParamsString()) {
            appParams =
                BinaryRunner.buildAppParams(this.invocation.getParams(), this.mpiDef.getParams(), pythonInterpreter);
        }

        // Calculate binary-streams redirection
        StdIOStream streamValues = new StdIOStream();
        ArrayList<String> binaryParams = BinaryRunner.createCMDParametersFromValues(this.invocation.getParams(),
            this.invocation.getTarget(), streamValues, pythonInterpreter);

        // MPI Flags
        String mpiFlags = mpiDef.getMpiFlags();
        int numMPIFlags = 0;
        String[] mpiflagsArray = null;
        if (mpiFlags != null && !mpiFlags.isEmpty() && !mpiFlags.equals("[unassigned]")) {
            mpiflagsArray = mpiFlags.split(" ");
            numMPIFlags = mpiflagsArray.length;
        }

        // Prepare command
        int cmdLength = NUM_BASE_MPI_ARGS + numMPIFlags;
        if (this.mpiDef.hasParamsString()) {
            cmdLength += appParams.length;
        } else {
            cmdLength += binaryParams.size();
        }
        String[] cmd = new String[cmdLength];

        int pos = 0;
        cmd[pos++] = this.mpiDef.getMpiRunner();
        cmd[pos++] = this.mpiDef.getHostsFlag();
        try {
            cmd[pos++] =
                this.mpiDef.generateHostsDefinition(this.taskSandboxWorkingDir, this.hostnames, this.computingUnits);
        } catch (IOException ioe) {
            throw new InvokeExecutionException("ERROR: writting hostfile", ioe);
        }
        cmd[pos++] = "-n";
        cmd[pos++] = this.mpiDef.generateNumberOfProcesses(this.numWorkers, this.computingUnits);

        for (int i = 0; i < numMPIFlags; ++i) {
            cmd[pos++] = mpiflagsArray[i];
        }

        cmd[pos++] = this.mpiDef.getBinary();

        // if params string is not null, all the params should be included there
        if (this.mpiDef.hasParamsString()) {
            for (String appParam : appParams) {
                cmd[pos++] = appParam;
            }
        } else {
            for (String binParam : binaryParams) {
                cmd[pos++] = binParam;
            }
        }

        // Prepare environment
        if (this.invocation.isDebugEnabled()) {
            PrintStream outLog = context.getThreadOutStream();
            outLog.println("");
            outLog.println("[MPI INVOKER] Begin MPI call to " + this.mpiDef.getBinary());
            outLog.println("[MPI INVOKER] On WorkingDir : " + this.taskSandboxWorkingDir.getAbsolutePath());
            // Debug command
            outLog.print("[MPI INVOKER] MPI CMD: ");
            for (String s : cmd) {
                outLog.print(s + " ");
            }
            outLog.println("");
            outLog.println("[MPI INVOKER] MPI STDIN: " + streamValues.getStdIn());
            outLog.println("[MPI INVOKER] MPI STDOUT: " + streamValues.getStdOut());
            outLog.println("[MPI INVOKER] MPI STDERR: " + streamValues.getStdErr());
        }

        // Launch command
        this.br = new BinaryRunner();
        return this.br.executeCMD(cmd, streamValues, this.taskSandboxWorkingDir, this.context.getThreadOutStream(),
            this.context.getThreadErrStream(), null, this.mpiDef.isFailByEV());
    }

    @Override
    public void cancelMethod() {
        LOGGER.debug("Cancelling MPI process");
        if (this.br != null) {
            this.br.cancelProcess();
        }
    }

    @Override
    protected void setEnvironmentVariables() {
        super.setEnvironmentVariables();
        int ppn = mpiDef.getPPN();
        if (LOGGER.isDebugEnabled()){
            System.out.println("[MPI INVOKER] OVERWRITING COMPSS_NUM_PROCS: " + this.computingUnits);
        }
        System.setProperty(COMPSS_NUM_PROCS, String.valueOf(this.computingUnits));

        if (ppn > 1) {
            int threads = this.computingUnits / ppn;
            System.setProperty(COMPSS_NUM_THREADS, String.valueOf(threads));
            System.setProperty(OMP_NUM_THREADS, String.valueOf(threads));

            // LOG ENV VARS
            if (LOGGER.isDebugEnabled()) {
                System.out.println("[MPI INVOKER] OVERWRITING COMPSS_NUM_THREADS: " + threads);
            }
        }
    }

}
