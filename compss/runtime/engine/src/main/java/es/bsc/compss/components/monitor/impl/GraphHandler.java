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


/**
 * Interface to handle additions to the monitoring graph.
 **/
public interface GraphHandler {

    void openTaskGroup(String groupName);

    void closeTaskGroup();

    /**
     * Closes a commutative group in the graph.
     *
     * @param group group to close in the graph.
     */
    public void closeCommutativeTasksGroup(CommutativeGroupTask group);

    void startTaskAnalysis(Task currentTask);

    /**
     * Adds a task in a commutative Group.
     *
     * @param task Task to be drawn in the graph
     * @param group group to whom the task belongs.
     */
    public void taskBelongsToCommutativeGroup(Task task, CommutativeGroupTask group);

    void startGroupingEdges();

    void stopGroupingEdges();

    /**
     * Adds edges to graph.
     *
     * @param consumer Consumer task
     * @param daId DataAccess causing the dependency
     * @param producer Producer task
     */
    public void addStandandDependency(Task consumer, DataAccessId daId, AbstractTask producer);

    /**
     * Adds the stream node and edge to the graph.
     *
     * @param task Writer or reader task.
     * @param streamDataId id of the stream generating the edge
     * @param isWrite Whether the task is reading or writing the stream parameter.
     */
    public void addStreamDependency(AbstractTask task, Integer streamDataId, boolean isWrite);

    void endTaskAnalysis(Task task, boolean taskHasEdge);

    /**
     * We have accessed to data produced by a task from the main code STEPS: Adds a new synchronization point if any
     * task has been created Adds a dependency from task to synchronization.
     *
     * @param task Task that generated the value.
     * @param edgeType Type of edge for the DOT representation.
     * @param accessedData Data being accessed
     */
    public void mainAccessToData(AbstractTask task, EdgeType edgeType, DataInstanceId accessedData);

    void groupBarrier(BarrierGroupRequest barrier);

    void barrier(Map<Integer, DataAccessesInfo> accessesInfo);

    void endApp();

    BufferedWriter getAndOpenCurrentGraph();

    void closeCurrentGraph();

    void removeCurrentGraph();
}
