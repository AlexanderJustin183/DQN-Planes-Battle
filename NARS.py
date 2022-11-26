#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
import subprocess
import threading


class NARS:
    def __init__(self, nars_type):  # nars_type: "OpenNars" or "ONA"
        self.read_line_thread = None
        self.process = None
        self.inference_cycle_frequency = 1  # set too large will get delayed and slow down the game
        self.operation_left = False
        self.operation_right = False
        self.operation_fire = False
        self.type = nars_type
        self.launch_nars()
        self.launch_thread()
    
    def launch_nars(self):
        self.process = subprocess.Popen(
            ["cmd"], bufsize=1,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            universal_newlines=True, encoding="utf-8", shell=False
        )
        if self.type == "OpenNars":
            self.add_to_cmd("java -Xmx1024m -jar OpenNars.jar")
        elif self.type == "ONA":
            self.add_to_cmd("NAR shell")
        self.add_to_cmd("*volume=0")
    
    def launch_thread(self):
        self.read_line_thread = threading.Thread(target=self.read_line,
                                                 args=(self.process.stdout,))
        self.read_line_thread.daemon = True
        # thread dies with the exit of the program
        self.read_line_thread.start()
    
    def read_line(self, out):
        pass
    
    def process_kill(self):
        # self.process.send_signal(signal.CTRL_C_EVENT)
        os.system("TASKKILL /f /im java.exe")
        # self.process.terminate()
    
    def babble(self):
        pass
    
    def add_to_cmd(self, string):
        self.process.stdin.write(string + "\n")
        self.process.stdin.flush()
    
    def add_inference_cycles(self, num):
        self.process.stdin.write(f"{num}\n")
        self.process.stdin.flush()
    
    def update(self, hero, enemy_group):
        # update sensors (object positions), remind goals, and make inference
        self.update_sensors(hero, enemy_group)
        self.remind_goal()
        # self.add_inference_cycles(self.inference_cycle_frequency)
    
    def update_sensors(self, hero, enemy_group):
        enemy_left = False
        enemy_right = False
        enemy_ahead = False
        for enemy in enemy_group.sprites():
            if enemy.rect.right < hero.rect.centerx:
                enemy_left = True
            elif hero.rect.centerx < enemy.rect.left:
                enemy_right = True
            elif enemy.rect.left <= hero.rect.centerx <= enemy.rect.right:
                enemy_ahead = True
        if enemy_left:
            self.add_to_cmd("<{enemy} --> [left]>. :|:")
        if enemy_right:
            self.add_to_cmd("<{enemy} --> [right]>. :|:")
        if enemy_ahead:
            self.add_to_cmd("<{enemy} --> [ahead]>. :|:")
    
    def valid_move(self):
        assert self.operation_right + self.operation_left < 2, "The plane can't move left and right."
    
    def move_left(self):  # NARS gives <(*,{SELF}) --> ^left>. :|:
        self.valid_move()
        self.operation_left = True
        self.operation_right = False
        print("move left")
    
    def move_right(self):  # NARS gives <(*,{SELF}) --> ^right>. :|:
        self.valid_move()
        self.operation_left = False
        self.operation_right = True
        print("move right")
    
    def do_not_move(self):  # NARS gives <(*,{SELF}) --> ^deactivate>. :|:
        self.valid_move()
        self.operation_left = False
        self.operation_right = False
        print("stay still")
    
    def fire(self):  # NARS gives <(*,{SELF}) --> ^strike>. :|:
        self.operation_fire = True
        print("fire")
    
    def remind_goal(self):
        self.add_to_cmd("<{SELF} --> [good]>! :|:")
    
    def praise(self):
        self.add_to_cmd("<{SELF} --> [good]>. :|:")
    
    def punish(self):
        self.add_to_cmd("(--,<{SELF} --> [good]>). :|:")
        # self.add_to_cmd("<{SELF} --> [good]>. :|: %0%")  # OpenNars' grammar
        # self.add_to_cmd("<{SELF} --> [good]>. :|: {0}")  # ONA's grammar


class ONA(NARS):
    def __init__(self):
        super().__init__("ONA")
        self.inference_cycle_frequency = 0
    
    def read_line(self, out):  # read line without blocking
        for line in iter(out.readline, b"\n"):  # get operations
            if (line[0] == "^"):
                operation = line.split(" ", 1)[0]
                if operation == "^left":
                    self.move_left()
                elif operation == "^right":
                    self.move_right()
                elif operation == "^deactivate":
                    self.do_not_move()
                elif operation == "^fire":
                    self.fire()
                else:
                    raise RuntimeError("[ERROR CODE 0] No current command.")
        out.close()


class OpenNars(NARS):
    def __init__(self):
        super().__init__("OpenNars")
        self.inference_cycle_frequency = 5
    
    def read_line(self, out):  # read line without blocking
        for line in out.readlines():  # get operations
            if line[0:3] == "EXE":
                sub_line = line.split(" ", 2)[2]
                operation = sub_line.split("(", 1)[0]
                if operation == "^left":
                    self.move_left()
                elif operation == "^right":
                    self.move_right()
                elif operation == "^deactivate":
                    self.do_not_move()
                elif operation == "^strike":
                    self.fire()
                else:
                    raise RuntimeError("[ERROR CODE 0] No current command.")
        out.close()
    
    def babble(self):
        # rand = random.choice(["left", "right", "none", "fire", "fire"])
        rand = random.randint(0, 6)
        if rand == 0:
            self.move_left()
            self.add_to_cmd("<(*,{SELF}) --> ^left>. :|:")
        if rand == 1:
            self.move_right()
            self.add_to_cmd("<(*,{SELF}) --> ^right>. :|:")
        if rand == 2:
            self.do_not_move()
            self.add_to_cmd("<(*,{SELF}) --> ^deactivate>. :|:")
        else:
            self.fire()
            self.add_to_cmd("<(*,{SELF}) --> ^strike>. :|:")
            