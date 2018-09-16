import random

# for step 1
class rgv_system_step_1:

    def __init__(self, m1, m2, m3, cw, c1, c2, dt, ut, wt, break_cond, cnc_set):
        self.move_time = [0, m1, m2, m3]
        self.cnc_work_time = cw
        self.ud_cnc_time = [dt, ut, dt, ut, dt, ut, dt, ut]
        self.washing_time = wt
        self.done_tot = 0
        self.rgv_pos = 0
        self.cnc_remaining_time = [0 for i in range(0, 8)]
        self.cur_time = 0 # in second
        self.has_break = break_cond
        self.done_time = []
        self.max_learning_time = 3600 # 1 hours
        self.max_working_time = 8 * 60 * 60 # 8 hours
        self.first_time = [True for i in range(0, 8)]
        self.broken_ones = [False for i in range(0, 8)]

    def whether_done(self):
        return self.cur_time > self.max_working_time

    def move_to(self, target):
        ret = self.move_time[max(target, self.rgv_pos) - min(target, self.rgv_pos)]
        self.rgv_pos = target
        return ret

    def state(self):
        return self.cnc_remaining_time + [self.rgv_pos]

    def global_working_ratio(self):
        if self.cur_time == 0: return 0
        return float(self.done_tot) / float(self.cur_time / 3600.0)

    def working_ratio(self):
        done_counter = 0
        for i in range(len(self.done_time) - 1, -1, -1):
            if self.cur_time - self.done_time[i] < self.max_learning_time:
                done_counter += 1
            else:
                break
        return done_counter

    def time_passing(self, sec):
        self.cur_time += sec
        if sec == 0:
            return
        for i in range(0, 8):
            self.cnc_remaining_time[i] = max(0, self.cnc_remaining_time[i] - sec)

    def eval(self, a, b):
        sec = 0
        sec += self.move_time[abs(a / 2 - self.rgv_pos)]
        sec += self.ud_cnc_time[a]
        sec += self.washing_time
        sec += self.move_time[abs(a / 2 - b / 2)]
        return sec < self.cnc_remaining_time[b]

    def check_usage(self, cnc_id):
        if self.cnc_remaining_time[cnc_id] == 0: return False
        for i in range(0, 8):
            if self.cnc_remaining_time[i] == 0 and self.eval(i, cnc_id):
                return True
        return False

    def take(self, cnc_id):
        useless_step = self.check_usage(cnc_id)

        # move and wait
        self.time_passing(self.move_to(cnc_id / 2))
        self.time_passing(self.cnc_remaining_time[cnc_id])

        # up
        rtn_time = self.cur_time
        self.time_passing(self.ud_cnc_time[cnc_id])

        # break
        this_one_break = False
        broken_time = 0
        if self.has_break and random.randint(1, 100) == 1:
            this_one_break = True
            broken_time = random.randint(1, self.cnc_work_time) + random.randint(10, 20)
            self.cnc_remaining_time[cnc_id] = broken_time
        else:
            self.cnc_remaining_time[cnc_id] = self.cnc_work_time
            self.done_time.append(self.cur_time)

        # wash and send
        if self.broken_ones[cnc_id] == True:
            pass
        else:
            if not self.first_time[cnc_id]:
                self.time_passing(self.washing_time)
                self.done_tot += 1
            else:
                self.first_time[cnc_id] = False
        self.broken_ones[cnc_id] = this_one_break
        return useless_step, [cnc_id, broken_time]

# for step 2
class rgv_system_step_2(rgv_system_step_1):

    # 0 for step 1, 1 for step 2
    def __init__(self, m1, m2, m3, cw, c1, c2, dt, ut, wt, break_cond, cnc_set):
        rgv_system_step_1.__init__(self, m1, m2, m3, cw, c1, c2, dt, ut, wt, break_cond, cnc_set)
        self.c1 = c1; self.c2 = c2; self.s2_only = False
        self.cnc_setting = []
        for i in range(0, 8):
            if cnc_set[i] == '1': self.cnc_setting.append(1)
            else: self.cnc_setting.append(0)

    def take(self, cnc_id):
        if self.s2_only == True and self.cnc_setting[cnc_id] == 0:
            return True, [0, 0] # useless_step
        elif self.s2_only == False and self.cnc_setting[cnc_id] == 1:
            return True, [0, 0]

        # move and wait
        self.time_passing(self.move_to(cnc_id / 2))
        self.time_passing(self.cnc_remaining_time[cnc_id])

        # up
        rtn_time = self.cur_time
        self.time_passing(self.ud_cnc_time[cnc_id])
 
        broken_time = 0
        if self.s2_only:
            # break
            this_one_break = False
            if self.has_break and random.randint(1, 100) == 1:
                this_one_break = True
                broken_time = random.randint(1, self.c2) + random.randint(10, 20)
                self.cnc_remaining_time[cnc_id] = broken_time
            else:
                self.cnc_remaining_time[cnc_id] = self.c2
                self.done_time.append(self.cur_time)

            # wash and send
            if self.broken_ones[cnc_id] == True:
                pass
            else:
                self.time_passing(self.washing_time)
                self.done_tot += 1
            self.broken_ones[cnc_id] = this_one_break
            self.s2_only = False
        else:
            # break
            this_one_break = False
            if self.has_break and random.randint(1, 100) == 1:
                this_one_break = True
                broken_time = random.randint(1, self.c2) + random.randint(10, 20)
                self.cnc_remaining_time[cnc_id] = broken_time
            else:
                self.cnc_remaining_time[cnc_id] = self.c1

            if self.broken_ones[cnc_id] == True:
                self.s2_only = False
            else:
                self.s2_only = True
            self.broken_ones[cnc_id] = this_one_break
        return False, [cnc_id, broken_time]
