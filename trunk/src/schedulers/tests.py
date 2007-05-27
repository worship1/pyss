#!/usr/bin/env python2.3

import unittest 
from simulator import * 


class test_Simulator(unittest.TestCase):

    def test_basic_cons_junk(self):
        simulator = Simulator(scheduler ="Fcfs", input_file = "./Input_test_files/basic_input.0")
        self.assertEqual(True, simulator.feasibilty_check_of_data())
        for job in simulator.jobs:
            self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)
                       

    def test_basic_fcfs(self):
        for i in range(25): 
            simulator = Simulator(scheduler ="Fcfs", input_file = "./Input_test_files/basic_input." + str(i))
            self.assertEqual(True, simulator.feasibilty_check_of_data())
            for job in simulator.jobs:
                # The job id in these specific test input files signifies the job correct finishing time:  
                # We use this basic idea to enable complex testing scenarios without much expansion of the code 
                self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)

    def test_basic_conservative(self):
        for i in range(25): 
            simulator = Simulator(scheduler ="Conservative", input_file = "./Input_test_files/basic_input." + str(i))
            self.assertEqual(True, simulator.feasibilty_check_of_data())
            for job in simulator.jobs:
                self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)
    
    def test_basic_easyBackfill(self):
        for i in range(25): 
            simulator = Simulator(scheduler ="EasyBackfill", input_file = "./Input_test_files/basic_input." + str(i))
            self.assertEqual(True, simulator.feasibilty_check_of_data())
            for job in simulator.jobs:
                self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)

    def test_basic_maui(self):
        for i in range(25): 
            simulator = Simulator(scheduler ="Maui", input_file = "./Input_test_files/basic_input." + str(i))
            self.assertEqual(True, simulator.feasibilty_check_of_data())
            for job in simulator.jobs:
                self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)
    


    def test_fcfs(self):
        for i in range(8): 
            simulator = Simulator(scheduler ="Fcfs", input_file = "./Input_test_files/fcfs_input." + str(i))
            self.assertEqual(True, simulator.feasibilty_check_of_data())
            for job in simulator.jobs:
                self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)



    def test_conservative(self):
        for i in range(9): 
            simulator = Simulator(scheduler ="Conservative", input_file = "./Input_test_files/bf_input." + str(i))
            self.assertEqual(True, simulator.feasibilty_check_of_data())
            for job in simulator.jobs:
                self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)

        for i in range(2): 
            simulator = Simulator(scheduler ="Conservative", input_file = "./Input_test_files/cons_bf_input." + str(i))
            self.assertEqual(True, simulator.feasibilty_check_of_data())
            for job in simulator.jobs:
                self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)
        
    
    
    def test_easyBackfill(self):
        for i in range(9): 
            simulator = Simulator(scheduler ="EasyBackfill", input_file = "./Input_test_files/bf_input." + str(i))
            self.assertEqual(True, simulator.feasibilty_check_of_data())
            for job in simulator.jobs:
                self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)

        for i in range(1): 
            simulator = Simulator(scheduler ="EasyBackfill", input_file = "./Input_test_files/easy_bf_input." + str(i))
            self.assertEqual(True, simulator.feasibilty_check_of_data())
            for job in simulator.jobs:
                self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)
                
                
    # below we test the weigths of maui: w_wtime, w_sld, w_user, w_bypass, w_admin, w_size
     
    def test_maui_wtime(self):
        # here we basically test that the maui with the default weights behaves as the easybackfill
        for i in range(9):
            simulator = Simulator(scheduler ="Maui", input_file = "./Input_test_files/bf_input." + str(i))
            self.assertEqual(True, simulator.feasibilty_check_of_data())
            for job in simulator.jobs:
                self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)

        for i in range(1): 
            simulator = Simulator(scheduler ="Maui", input_file = "./Input_test_files/easy_bf_input." + str(i))
            self.assertEqual(True, simulator.feasibilty_check_of_data())
            for job in simulator.jobs:
                self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)

    def test_maui_wait_and_size(self):
        # testing w_size = number of nodes (vs. w_wait):
        # (w_wtime, w_sld, w_user, w_bypass, w_admin, w_size)
        w_l = Weights(1, 0, 0, 0, 0, 0)
        w_b = Weights(0, 0, 0, 0, 0, -1) 
        
        simulator = Simulator(scheduler ="Maui", maui_list_weights = w_l, maui_backfill_weights = w_b, \
                              input_file = "./Input_test_files/maui.size")
        self.assertEqual(True, simulator.feasibilty_check_of_data())
        for job in simulator.jobs:
            self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)

    def test_maui_admin_vs_userQoS(self):
        # testing the w_admin = admin QoS and w_user = user QoS:
        # (w_wtime, w_sld, w_user, w_bypass, w_admin, w_size)
        w_l = Weights(0, 0, 0, 0, 1, 0)
        w_b = Weights(0, 0, 1, 0, 0, 0) 
        
        simulator = Simulator(scheduler ="Maui", maui_list_weights = w_l, maui_backfill_weights = w_b, \
                              input_file = "./Input_test_files/maui.admin_vs_user")
        self.assertEqual(True, simulator.feasibilty_check_of_data())
        for job in simulator.jobs:
            self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)

    def test_maui_bypass_vs_slow_down(self):
        # testing the w_admin = admin QoS and w_user = user QoS:
        # (w_wtime, w_sld, w_user, w_bypass, w_admin, w_size)
        w_l = Weights(0, 0, 0, 1, 1, 0) 
        w_b = Weights(0, 1.0, 0, 0, 0, 0) 
        
        simulator = Simulator(scheduler ="Maui", maui_list_weights = w_l, maui_backfill_weights = w_b, \
                              input_file = "./Input_test_files/maui.bypass_vs_sld")
        self.assertEqual(True, simulator.feasibilty_check_of_data())
        for job in simulator.jobs:
            self.assertEqual(int(float(job.id)), job.start_to_run_at_time + job.actual_run_time)


###########





if __name__ == "__main__":
    unittest.main()
