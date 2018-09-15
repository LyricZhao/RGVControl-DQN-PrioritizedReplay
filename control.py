# for step 1
import random

class rgv_system_step_1:

    def __init__(self, m1, m2, m3, cw, dt, ut, wt, break_cond):
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

        '''
        print 'move_time = ', self.move_time
        print 'cnc_work_time = ', self.cnc_work_time
        print 'ud_cnc_time = ', self.ud_cnc_time
        print 'washing time = ', self.washing_time
        print 'break = ', break_cond
        '''

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
        min_time = 0
        for i in range(len(self.done_time) - 1, -1, -1):
            if self.cur_time - self.done_time[i] < self.max_learning_time:
                done_counter += 1
                min_time = self.done_time[i]
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
        self.time_passing(self.ud_cnc_time[cnc_id])

        # break
        if self.has_break and random.randint(1, 100) == 1:
            self.done_tot -= 1
            self.cnc_remaining_time[cnc_id] = random.randint(1, self.cnc_work_time) + random.randint(10, 20)
        else:
            self.cnc_remaining_time[cnc_id] = self.cnc_work_time
            self.done_time.append(self.cur_time)

        # wash and send
        self.time_passing(self.washing_time)
        self.done_tot += 1
        return useless_step
