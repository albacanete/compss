/*
 *  Copyright 2002-2019 Barcelona Supercomputing Center (www.bsc.es)
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
package es.bsc.compss.worker;

import java.util.TimerTask;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import es.bsc.compss.log.Loggers;

public class TimeOutTask extends TimerTask {

    protected static final Logger LOGGER = LogManager.getLogger(Loggers.WORKER_INVOKER);

    int taskId;
    
    public TimeOutTask(int taskId) {
        this.taskId = taskId;
    }
    
    @Override
    public void run() {
        LOGGER.info("The task " + taskId + " timed out");
        COMPSsWorker.setCancelled(taskId);

    }

}

