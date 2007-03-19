#!/usr/bin/env python2.4
from sim import * 

class Event:
    def __init__(self, job=None):
        self.job = job

class EndOfSimulationEvent(Event):
    def __str__(self):
        return "End of Simulation Event" 

class JobArrivalEvent(Event):
    def __str__(self):
        return "Job Arrival Event: " + str(self.job)

class JobTerminationEvent(Event):
     def __str__(self):
        return "Job Termination Event: " + str(self.job)


class JobArrivalEventGeneratorViaLogFile:
    
    def __init__(self, input_file):
        """Assumption: Job details are 'correct': arrival_time, nodes and duration are non-negative,

        and the amount of nodes requested by the job is never more than the total available nodes"""
        
        self.file = file(input_file) #open the specified file for reading 
        self.events = {}
        self.jobs = []
        
        while True: 
            line = self.file.readline()
            if len(line) == 0: # zero length indicates end-of-file
                break
            
            (job_arrival_time, job_id, job_duration, job_nodes, job_actual_duration ) = line.split()
            newJob = Job(job_id, int(job_duration), int(job_nodes), int(job_arrival_time), int(job_actual_duration))

            self.jobs.append(newJob) 
            newEvent = JobArrivalEvent(newJob)

            if self.events.has_key(int(job_arrival_time)):
                self.events[int(job_arrival_time)].append(newEvent)
            else:
                self.events[int(job_arrival_time)] = []
                self.events[int(job_arrival_time)].append(newEvent)    
        self.file.close()


    def printEvents(self):
        times = self.events.keys()
        times.sort()
        for t in times:
            for element in self.events[t]: 
                print element 
        print

            
        

class Simulator:
    """ Assumption: The simulation clock goes only forward. Specifically,
    an event on time t can only produce future events with time t' = t or t' > t."""
    
    def startSimulation(self):
        pass
    
    def __init__(self, total_nodes=100, input_file='input', scheduler="ConservativeScheduler"):
        self.total_nodes = total_nodes
        self.current_time = 0
        events_generated_by_input_file = JobArrivalEventGeneratorViaLogFile(input_file)
        self.events = events_generated_by_input_file.events
        self.jobs = events_generated_by_input_file.jobs
        # self.scheduler =  ConservativeScheduler(total_nodes)
        self.scheduler =  EasyBackfillScheduler(total_nodes)
        self.startSimulation()

    def addEvent(self, time, event):
         if self.events.has_key(time):
             self.events[time].append(event)
         else:
             self.events[time] = []
             self.events[time].append(event)
    
    def addEvents(self, events_dictionary):
         for new_time, new_event in events_dictionary.iteritems():             
             if isinstance(new_event, JobTerminationEvent): #del prev termination event
                 found = False
                 for time, list_of_events_at_this_time in self.events.iteritems():
                     if found:
                         break 
                     for event in self.events[time]:
                         if event.job.id == new_event.job.id and isinstance(event, JobTerminationEvent):
                             list_of_events_at_this_time.remove(event)
                             print "_____ old job termination event at time", time
                             print "_____ new job termination event at time", new_time 
                             found = True
                             break
                 self.addEvent(new_time, new_event)

             else:
                 self.addEvent(time, new_event)
                 
    def test(self):
        pass
    
    def startSimulation(self):
        """ Assumption1: times are non-negative numbers. """

        end_of_simulation_event_has_not_occured = True 

        while end_of_simulation_event_has_not_occured and len(self.events) > 0:
 
            times_of_events = self.events.keys() #*** I couldn't do the sorting nicely as Ori suggested 
            times_of_events.sort()
            current_time = times_of_events.pop(0)

            while len(self.events[current_time]) > 0:
                self.scheduler.cpu_snapshot.printCpuSlices()

                event = self.events[current_time].pop()
                print str(event)

                if isinstance(event, JobArrivalEvent):
                    newEvents = self.scheduler.handleArrivalOfJobEvent(event.job, int(current_time))
                    self.addEvents(newEvents) 
                    continue

                elif isinstance(event, JobTerminationEvent):
                    newEvents = self.scheduler.handleTerminationOfJobEvent(event.job, current_time)
                    self.addEvents(newEvents)
                    continue

                elif isinstance(event, EndOfSimulationEvent):
                    end_of_simulation_event_has_not_occured = False 
                    break

                else:
                    assert False # should never reach here
                
            
            del self.events[current_time] #removing the events that were just handled
            
        self.scheduler.cpu_snapshot.printCpuSlices()

        print "____ feasibility check starts now: _______" 
        if self.isFeasibleSchedule():
            print "Feasibility Test is OK!!!!!"
        else: 
            print "!!!!!!!!!! There is a problem with the feasibilty of the simulator/schedule !!!!!!!!"
          

        
    def isFeasibleSchedule(self):
        """ check the feasibility of the schedule produced by the simulation. """
        
        cpu_snapshot = CpuSnapshot(self.total_nodes)
        for job in self.jobs:
            print str(job)
            if job.arrival_time > job.start_to_run_at_time:
                print "PROBLEM: job starts before arrival...."
                return False
            if job.actual_duration > 0:
                new_job = Job(job.id, job.actual_duration, job.nodes, job.arrival_time, job.actual_duration)
                cpu_snapshot.assignJob(new_job, job.start_to_run_at_time)
                cpu_snapshot.printCpuSlices()
                
        cpu_snapshot.printCpuSlices()
        return cpu_snapshot.CpuSlicesTestFeasibility()
    
        
        
        
class Scheduler:        
     def handleArrivalOfJobEvent(self, job, time):
         pass
     def handleTerminationOfJobEvent(self, job, time):
         pass
     


class ConservativeScheduler(Scheduler):

    def __init__(self, total_nodes = 100):
        self.cpu_snapshot = CpuSnapshot(total_nodes)
        self.list_of_unfinished_jobs_arranged_by_arrival_times = []

        
    def handleArrivalOfJobEvent(self, job, time):
        self.list_of_unfinished_jobs_arranged_by_arrival_times.append(job)        
        start_time_of_job = self.cpu_snapshot.jobEarliestAssignment(job, time)
        self.cpu_snapshot.assignJob(job, start_time_of_job)
        newEvent ={}
        new_event = JobTerminationEvent(job)
        termination_time = job.start_to_run_at_time + job.actual_duration
        newEvent[termination_time] = new_event                
        return newEvent
    
    def handleTerminationOfJobEvent(self, job, time):
        """ this handler deletes the tail of job if it was ended before the duration declaration.
        It then reschedule the remaining jobs and returns a collection of new termination events
        (using the dictionary data structure) """
        self.list_of_unfinished_jobs_arranged_by_arrival_times.remove(job)
        if job.actual_duration < job.user_predicted_duration: 
            self.cpu_snapshot.delTailofJobFromCpuSlices(job)
            return self.reschedule_jobs(time)
        else:
            return {}


    def reschedule_jobs(self, time):

        newEvents ={}

        for job in self.list_of_unfinished_jobs_arranged_by_arrival_times:

            if job.start_to_run_at_time <= time:
                continue # job started to run before, so it cannot be rescheduled (preemptions are not allowed)

            prev_start_to_run_at_time = job.start_to_run_at_time
            self.cpu_snapshot.delJobFromCpuSlices(job)
            start_time_of_job = self.cpu_snapshot.jobEarliestAssignment(job, time)
            self.cpu_snapshot.assignJob(job, start_time_of_job)
            if prev_start_to_run_at_time > job.start_to_run_at_time:
                new_event = JobTerminationEvent(job)
                new_termination_time = job.start_to_run_at_time + job.actual_duration
                newEvents[new_termination_time] = new_event
                
        return newEvents
                
                

class EasyBackfillScheduler(Scheduler):
    def __init__(self, total_nodes = 100):
        self.cpu_snapshot = CpuSnapshot(total_nodes)
        self.waiting_list_of_unscheduled_jobs_arranged_by_arrival_times = []

    def canBeBackfilled(self, first_job, second_job, time):
        start_time_of_first_job = self.cpu_snapshot.jobEarliestAssignment(first_job, time)
        
        start_time_of_second_job = self.cpu_snapshot.jobEarliestAssignment(second_job, time)
        # TODO: shouldn't this method not change the state?
        self.cpu_snapshot.assignJob(second_job, start_time_of_second_job)
        start_time_of_first_job_after_assigning_the_second_job = self.cpu_snapshot.jobEarliestAssignment(first_job, time)

        self.cpu_snapshot.delJobFromCpuSlices(second_job)
       
        if start_time_of_first_job_after_assigning_the_second_job > start_time_of_first_job:
            print "start_time_of_first_job", start_time_of_first_job
            print "start_time_of_first_job_after_assigning_the_second_job", start_time_of_first_job_after_assigning_the_second_job
            return False 
                #this means that assigning the second job at the earliest possible time postphones the
                #first job in the waiting list, and so we postphone the scheduling of the second job
        else:
            return True 
      

        
    def handleArrivalOfJobEvent(self, just_arrived_job, time):
             
        if len(self.waiting_list_of_unscheduled_jobs_arranged_by_arrival_times) == 0:
            first_job = just_arrived_job
        else: 
            first_job = self.waiting_list_of_unscheduled_jobs_arranged_by_arrival_times[0]
            
        newEvent = emptyEvent = {}
        
        if first_job.id != just_arrived_job.id: # two distinct jobs
            
            if self.canBeBackfilled(first_job, just_arrived_job, time):
                print "JOB CAN BE BACKFILLED!!!! LA LA LA"
                start_time_of_just_arrived_job = self.cpu_snapshot.jobEarliestAssignment(just_arrived_job, time)
                self.cpu_snapshot.assignJob(just_arrived_job, start_time_of_just_arrived_job)
                new_event = JobTerminationEvent(just_arrived_job)
                termination_time = just_arrived_job.start_to_run_at_time + just_arrived_job.actual_duration
                newEvent[termination_time] = new_event                
                return newEvent  

            else:
                self.waiting_list_of_unscheduled_jobs_arranged_by_arrival_times.append(just_arrived_job)
                return emptyEvent 
 
        
        else: # the just arrived job is the only job (to be scheduled soon) that we now have in the waiting list 
             start_time_of_just_arrived_job = self.cpu_snapshot.jobEarliestAssignment(just_arrived_job, time)
             if start_time_of_just_arrived_job == time:
                 self.cpu_snapshot.assignJob(just_arrived_job, time)
                 new_event = JobTerminationEvent(just_arrived_job)
                 termination_time = time + just_arrived_job.actual_duration
                 newEvent[termination_time] = new_event                
                 return newEvent
             else:
                 self.waiting_list_of_unscheduled_jobs_arranged_by_arrival_times.append(just_arrived_job)
                 return emptyEvent
             
                 

    def handleTerminationOfJobEvent(self, job, time):
        """ this handler deletes the tail of job if it was ended before the duration declaration.
        It then reschedule the remaining jobs and returns a collection of new termination events
        (using the dictionary data structure) """

        if job.actual_duration < job.user_predicted_duration: 
            self.cpu_snapshot.delTailofJobFromCpuSlices(job)
        
        return self.schedule_jobs(time)



    def schedule_jobs(self, time):
        newEvents = emptyEvent = {}
                             
        if len(self.waiting_list_of_unscheduled_jobs_arranged_by_arrival_times) == 0:
            return emptyEvent # waiting list is empty        

        #first, try to schedule the head of the waiting list
        while len(self.waiting_list_of_unscheduled_jobs_arranged_by_arrival_times) > 0: 
            first_job = self.waiting_list_of_unscheduled_jobs_arranged_by_arrival_times[0]
            start_time_of_first_job = self.cpu_snapshot.jobEarliestAssignment(first_job, time)
            if start_time_of_first_job == time:
                self.waiting_list_of_unscheduled_jobs_arranged_by_arrival_times.remove(first_job)
                self.cpu_snapshot.assignJob(first_job, time)
                new_event = JobTerminationEvent(first_job)
                termination_time = time + first_job.actual_duration
                newEvents[termination_time] = new_event                
            else:
                break

        #then, try to backfill the tail of the waiting list
        if len(self.waiting_list_of_unscheduled_jobs_arranged_by_arrival_times) > 1:
            first_job = self.waiting_list_of_unscheduled_jobs_arranged_by_arrival_times[0]
            for next_job in self.waiting_list_of_unscheduled_jobs_arranged_by_arrival_times[1:] : 
                if self.canBeBackfilled(first_job, next_job, time):
                    self.waiting_list_of_unscheduled_jobs_arranged_by_arrival_times.remove(next_job)
                    start_time_of_next_job = self.cpu_snapshot.jobEarliestAssignment(next_job, time)
                    self.cpu_snapshot.assignJob(next_job, start_time_of_next_job)
                    new_event = JobTerminationEvent(next_job)
                    termination_time = next_job.start_to_run_at_time + next_job.actual_duration
                    newEvents[termination_time] = new_event                
        return newEvents
 
        
    
    
###############

sim = Simulator()

            
