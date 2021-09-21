#!/usr/bin/python
#
#
import os
import sys
import glob
from pathlib import Path
import shutil
import argparse
import datetime
import socket

    

class StdioRotate:
    def __init__(self):
        self.generations = 10
        self.log_pattern = ""
        self.file_out_base = ""
        self.file_out_first_genartion = ""
        self.header = False
    def _parse_args(self):
        self.parser = argparse.ArgumentParser(description='stdio rotation')
        self.parser.add_argument('--generations', help='number of outputs to keep ')
        self.parser.add_argument('--file', help='output prefix ')
        self.parser.add_argument('--header', action="store_true",
                                 help='Pre-append time/header to output')
        args = self.parser.parse_args()
        if args.generations:
            try:
                self.generations = int(args.generations)
            except:
                print("setting to 10 - invalid generations value")
        if args.file:
            self.file_out_base = args.file
        else:
            print("No output file specified  -- exiting")
            sys.exit(8)    
        if args.header:
            self.header = True
    # special arg processing if nec
    def rotate_generations(self):
        print("here1")
        gen = self.list_generations()
        if len(gen)  == 0:
             print("h2.1")
             new_file = self.file_out_base + ".1"
             print("new_file 1", new_file)
             shutil.copy(self.file_out_base, new_file)
        else:
            last_file = gen.pop()
            gen_num = self.parse_gen_number( self.file_out_base, last_file)
            if  gen_num == self.generations:
                os.remove(last_file)
                gen.append(last_file)
            if  gen_num < self.generations:
                incr_file = self.incr_rename_generation( last_file, gen_num)
                gen.append(last_file)
                gen.append(incr_file)
            while gen:
                if len(gen) > 1:
                    new_file = gen.pop()
                    last_file = gen.pop()
                    print("last_file(1):", last_file, new_file  )
                    shutil.copy( last_file, new_file)
                    gen.append( last_file)
                else:
                    last_file = self.file_out_base
                    new_file = gen.pop()
                    print("last_file:", last_file, new_file  )
                    shutil.copy( last_file, new_file)
                #last_file = new_file
            new_file = self.file_out_base + ".1"
            shutil.copy(self.file_out_base, new_file)
    def _create_glob(self):
        return self.file_out_base + ".*"
    def list_generations(self):
        glob_f = self._create_glob()
        generation_list = self.get_list_of_files(".", glob_f)
        return generation_list
    def run(self):
        self._parse_args()
        self._write_file()
        self.rotate_generations()
    def _write_header(self, f):
        if self.header == False:
            return
        t_begin = datetime.datetime.now()
        time_string = t_begin.strftime("%A, %d. %B %Y %I:%M%p")
        f.write("*" * 80 + "\n")
        f.write("*\n")
        f.write("* datetime: ")
        f.write(" " +  time_string + "\n")
        f.write("* system:   ")
        f.write(" " +  sys.platform + "\n")
        f.write("* host:     ")
        f.write(" " + socket.gethostname() + "\n") 
        f.write("* user:     ")
        f.write(" " +  os.getlogin() + "\n")
        f.write("*" + "\n")
        f.write("*" * 80 + "\n")
        return
        
    def _write_file(self):
        print("write_file")
        with open(self.file_out_base, mode = "w") as f:
            self._write_header(f)
            while True:
                input_ = sys.stdin.readline()
                if input_ == '':
                    print("exit")
                    break
                # print(input_)
                f.write(input_)
        return
    def last_3chars(self, x):
        file_l = x.split(".")
        try:
            ret = int(file_l.pop())
        except:
            print(" Invalid generation file:",  x)
            sys.exit(8)
        return ret

    def get_list_of_files(self, dir, glob_filter):
        glob_path = Path(dir)
        file_list = [str(pp) for pp in glob_path.glob(str(glob_filter))]
        final_l = []
        for f in file_list:
            final_l.append(os.path.split(f)[1])
        final_l.sort(key = self.last_3chars)
        return final_l

    def parse_gen_number( self, f_base, in_file):
        l = len(f_base)
        str_start = in_file[l:]
        print("str_start: ", str_start)
        str_start = str_start[1:]
        print('2nd ', str_start)
        try:
            gen_num = int(str_start[0:3])
        except:
            gen_num = -1
        return gen_num

    def incr_rename_generation(self, myfile, i ):
        i = i + 1
        file_l = myfile.split(".")
        file_l.pop()
        file_l.append(str(i))
        print(file_l)
        new_file = file_l.pop(0)
        print("new_file:", new_file)
        while file_l:
            new_file = new_file + "." + file_l.pop(0)
        print("final new:", new_file)
        return new_file
    
    
if __name__ == "__main__":
    sr = StdioRotate()
    sr.run()
   