/*         
 *  Copyright 2002-2018 Barcelona Supercomputing Center (www.bsc.es)
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
package es.bsc.compss.types.request.ap;

import java.util.concurrent.Semaphore;

import es.bsc.compss.components.impl.AccessProcessor;
import es.bsc.compss.components.impl.DataInfoProvider;
import es.bsc.compss.components.impl.TaskAnalyser;
import es.bsc.compss.components.impl.TaskDispatcher;

public class WaitForConcurrentRequest extends APRequest {

    private int dataId;
    private Semaphore sem;
    private Semaphore semTask;
    private int numWaits;

    public WaitForConcurrentRequest(int dataId, Semaphore sem, Semaphore semTasks) {
        this.dataId = dataId;
        this.sem = sem;
        this.semTask = semTasks;
                
    }

    public int getDataId() {
        return dataId;
    }

    public void setDataId(int dataId) {
        this.dataId = dataId;
    }

    @Override
    public void process(AccessProcessor ap, TaskAnalyser ta, DataInfoProvider dip, TaskDispatcher td) {
        ta.findWaitedConcurrent(this);
    }

    @Override
    public APRequestType getRequestType() {
        return APRequestType.WAIT_FOR_CONCURRENT;
    }

    public int getNumWaitedTasks() {
        return numWaits;
    }

    public void setNumWaitedTasks(int n) {
        numWaits=n;
    }

    public Semaphore getSemaphore() {
        return sem;    
    }

    public Semaphore getTaskSemaphore() {
        return semTask;
    }

}
