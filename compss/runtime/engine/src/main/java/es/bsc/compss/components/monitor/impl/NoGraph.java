/*
 *  Copyright 2002-2023 Barcelona Supercomputing Center (www.bsc.es)
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
package es.bsc.compss.components.monitor.impl;

import es.bsc.compss.types.AbstractTask;
import es.bsc.compss.types.CommutativeGroupTask;
import es.bsc.compss.types.Task;
import es.bsc.compss.types.accesses.DataAccessesInfo;
import es.bsc.compss.types.data.DataAccessId;
import es.bsc.compss.types.data.DataInstanceId;
import es.bsc.compss.types.request.ap.BarrierGroupRequest;

import java.io.BufferedWriter;
import java.util.Map;


public class NoGraph implements GraphHandler {

    /**
     * Constructs a new GraphHandler that won't do anything.
     */
    public NoGraph() {
    }

    @Override
    public final void openTaskGroup(String groupName) {
        // Do nothing
    }

    @Override
    public final void closeTaskGroup() {
        // Do nothing
    }

    @Override
    public final void closeCommutativeTasksGroup(CommutativeGroupTask group) {
        // Do nothing
    }

    @Override
    public final void startTaskAnalysis(Task currentTask) {
        // Do nothing
    }

    @Override
    public final void taskBelongsToCommutativeGroup(Task task, CommutativeGroupTask group) {
        // Do nothing
    }

    @Override
    public final void startGroupingEdges() {
        // Do nothing
    }

    @Override
    public final void stopGroupingEdges() {
        // Do nothing
    }

    @Override
    public final void addStandandDependency(Task consumer, DataAccessId daId, AbstractTask producer) {
        // Do nothing
    }

    @Override
    public final void addStreamDependency(AbstractTask task, Integer streamDataId, boolean isWrite) {
        // Do nothing
    }

    @Override
    public final void endTaskAnalysis(Task task, boolean taskHasEdge) {
        // Do nothing
    }

    @Override
    public final void mainAccessToData(AbstractTask task, EdgeType edgeType, DataInstanceId accessedData) {
        // Do nothing
    }

    @Override
    public final void groupBarrier(BarrierGroupRequest barrier) {
        // Do nothing
    }

    @Override
    public final void barrier(Map<Integer, DataAccessesInfo> accessesInfo) {
        // Do nothing
    }

    @Override
    public final void endApp() {
        // Do nothing
    }

    @Override
    public BufferedWriter getAndOpenCurrentGraph() {
        // Do nothing
        return null;
    }

    @Override
    public void closeCurrentGraph() {
        // Do nothing
    }

    @Override
    public final void removeCurrentGraph() {
        // Do nothing
    }
}
