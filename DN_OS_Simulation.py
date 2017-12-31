'''
# ****************************************************************
# ****************************************************************
    Daniyal Naeem
    CSCI 340 - OS
    Assignment -> Operating System Simulation
# ****************************************************************
# ****************************************************************
'''



'''
a new process is created with a priority
    - fetch priority
    - assign PID            - incremented before func call
    - assign TIMESTAMP      - incremented before func call
    - check for CPU access and CPU_queue
    - update FRAME_TABLE and NUM_OF_PAGES
    -
'''
# ****************************************************************
def new_process(user_cmd, PID, TIMESTAMP, FRAME_TABLE, pages_left, CPU_pid, CPU_priority, CPU_queue):
    #split the user_cmd, fetch new_priority
    data = user_cmd.split()
    new_priority = int(data[1])
    #push PID and priority onto FRAME_TABLE
    #if FRAME_TABLE is full, use LRU
    if pages_left == 0:
        #lru replacement
        #create a variable to store the index of the lRU Frame
        # - default, intialize to index of frame 0
        LRU_index = 0
        #create a variable to store the timestamp of the LRU frame
        # - default, initialize to TS frame 0
        LRU_ts = FRAME_TABLE[0]['TIMESTAMP']
        #go thru every frame in FRAME_TABLE
        for frame in range( len( FRAME_TABLE) ):
            #store timestamp of current frame
            curr_ts = FRAME_TABLE[frame]['TIMESTAMP']
            #if curr_ts is smaller
            if curr_ts < LRU_ts:
                #update LRU_ts
                LRU_ts = curr_ts
                #store index of LRU frame
                LRU_index = frame
            #end if
        #end for
        #replace frame @ LRU_index w/ new process info
        FRAME_TABLE[LRU_index] = {'PAGE' : 0, 'PID' : PID, 'TIMESTAMP' : TIMESTAMP}
    #else place at empty frame
    else:
        #decrement pages left
        pages_left -= 1
        #go thru FRAME_TABLE, look for empty frame
        for frame in range(len(FRAME_TABLE)):
            #if the len of the frame == 0
            if len(FRAME_TABLE[frame]) == 0:
                #empty frame found, insert data here
                FRAME_TABLE[frame] = {'PAGE' : 0, 'PID' : PID, 'TIMESTAMP' : TIMESTAMP}
                break
            #end if
        #end for
    #end if/else
    #check for cold start
    if CPU_pid == 0:
        #place process in cpu
        CPU_pid = PID
        CPU_priority = new_priority
    #else decide between preemption or ready queue
    else:
        #check for preemption
        if new_priority > CPU_priority:
            #store old CPU values
            temp_id = CPU_pid
            temp_priority = CPU_priority
            #overwrite with new CPU value
            CPU_pid = PID
            CPU_priority = new_priority
            #store old values
            PID = temp_id
            new_priority = temp_priority
        #place new pid and priority in queue
        CPU_queue[PID] = new_priority
    #end if/else
    #return altered values
    return pages_left, CPU_pid, CPU_priority
# ****************************************************************

'''
The process that currently uses the CPU terminates. It leaves the system immediately. Make sure you release the memory used by this process.
'''
# ****************************************************************
def terminate(CPU_pid, CPU_priority, CPU_queue, FRAME_TABLE, NUM_OF_PAGES, pages_left):
    #fetch pid
    terminate_pid = CPU_pid
    #place highest priority process from queue in CPU
    top_priority = 0
    top_pid = 0
    #if CPU_queue has content, find the highest priority
    if len(CPU_queue) > 0:
        #go thru queue
        for process in CPU_queue:
            #if priority @process is higher
            if CPU_queue[process] > top_priority:
                #extract values
                top_priority = CPU_queue[process]
                top_pid = process
            #end if
        #end for
        #remove from queue
        del CPU_queue[top_pid]
    #end if
    #place values @ CPU
    CPU_pid = top_pid
    CPU_priority = top_priority
    #free memory from FRAME_TABLE
    #go thru every frame
    for frame in range(NUM_OF_PAGES):
        #check if frame has content
        if len( FRAME_TABLE[frame] ) > 0:
            #if the pid matches, make empty, increment pages_left
            if terminate_pid == FRAME_TABLE[frame]['PID']:
                FRAME_TABLE[frame] = {}
                pages_left += 1
            #end if
        #end if
    #end for
    #return altered values
    return CPU_pid, CPU_priority, pages_left
# ****************************************************************

'''
    currently active process @CPU accesses hard disk
'''
# ****************************************************************
def disk_access(user_cmd, CPU_pid, CPU_priority, CPU_queue, HDD_table):
    #fetch disk and filename
    data = user_cmd.split()
    disk = int(data[1])
    file_name = data[2]
    #MANAGE CPU
    #extract pid and priority
    disk_pid = CPU_pid
    disk_priority = CPU_priority
    #place highest priority process from queue in CPU
    top_priority = 0
    top_pid = 0
    #if CPU_queue has content,find the highest priority
    if len(CPU_queue) > 0:
        #go thru queue
        for process in CPU_queue:
            #if priority @process is higher
            if CPU_queue[process] > top_priority:
                #extract values
                top_priority = CPU_queue[process]
                top_pid = process
            #end if
        #end for
        #remove from queue
        del CPU_queue[top_pid]
    #end if
    #place values @ CPU
    CPU_pid = top_pid
    CPU_priority = top_priority
    #manage hard disk
    #add pid, priority and filename to designated disk
    HDD_table[disk]['PID'].append(disk_pid)
    HDD_table[disk]['PRIORITY'].append(disk_priority)
    HDD_table[disk]['FILENAME'].append(file_name)
    #return altered values
    return CPU_pid, CPU_priority
# ****************************************************************
'''
    The hard disk #number has finished the work for one process
    go back to cpu
'''
# ****************************************************************
def disk_complete(user_cmd, HDD_table, CPU_pid, CPU_priority, CPU_queue):
    #fetch disk number
    data = user_cmd.split()
    disk = int(data[1])
    #check if the disk is being used
    if len(HDD_table[disk]['PID']) > 0:
        #fetch pid and priority (index 0)
        disk_pid = HDD_table[disk]['PID'][0]
        disk_priority = HDD_table[disk]['PRIORITY'][0]
        #delete the first item at the disk
        del HDD_table[disk]['PID'][0]
        del HDD_table[disk]['PRIORITY'][0]
        del HDD_table[disk]['FILENAME'][0]
        #place at disk process CPU or ready_queue
        #check for idle CPU
        if CPU_pid == 0:
            #place process in cpu
            CPU_pid = disk_pid
            CPU_priority = disk_priority
        #else decide between preemption or ready_queue
        else:
            #check for preemption
            if disk_priority > CPU_priority:
                #store old cpu values
                temp_id = CPU_pid
                temp_priority = CPU_priority
                #overwrite with enw CPU values
                CPU_pid = disk_pid
                CPU_priority = disk_priority
                #store old values
                disk_pid = temp_id
                disk_priority = temp_priority
            #place disk_pid and disk_priority in queue
            CPU_queue[disk_pid] = disk_priority
        #end if/else
    #end if
    #return altered values
    return CPU_pid, CPU_priority
# ****************************************************************

# ****************************************************************
def show_CPU(CPU_pid, CPU_priority, CPU_queue):
    print ' > CPU'
    print '  > PID          : ', CPU_pid
    print '  > Priority     : ', CPU_priority
    print '  > Ready Queue  : ', CPU_queue
# ****************************************************************

# ****************************************************************
def show_HDD(HDD_table):
    print ' > HDD Access'
    #go thru the disks
    for disk in range(NUM_OF_HDD):
        print '  > Disk', disk
        #find the length of the list @ [PID]
        length = len(HDD_table[disk]['PID'])
        #if there's at least one process at the disk
        if length >= 1:
            #print current (0th) process pid and filename
            print '   > Current process:'
            print '    > ',
            print HDD_table[disk]['PID'][0], ':',
            print HDD_table[disk]['FILENAME'][0]
        #if there are processes waiting at the disk
        if length >= 2:
            #print each element in pid and filename queue
            print '   > In queue:'
            for x in range(1, length):
                print '    > ',
                print HDD_table[disk]['PID'][x], ':',
                print HDD_table[disk]['FILENAME'][x]
# ****************************************************************

# ****************************************************************
def show_mem(FRAME_TABLE):
    print ' > FRAME TABLE'
    for frame in FRAME_TABLE:
        print '  > Frame', frame, FRAME_TABLE[frame]
# ****************************************************************

# ****************************************************************
'''
    - takes an input
    - divide by page size (integer division) -> page#
    - use CPU_pid, look thru FRAME_TABLE
    - if found, look for page#
    - if match, update lru if not found,
    - create new entry with pid
'''
def mem_acces(user_cmd, PAGE_SIZE, CPU_pid, FRAME_TABLE, pages_left, TIMESTAMP):
    #fetch mem address
    data = user_cmd.split()
    mem_address = int(data[1])
    #var for match
    match = 0
    #calculate page# (integer division)
    page_num = mem_address / PAGE_SIZE
    #go thru every frame, look for a matching PID
    for frame in range( len(FRAME_TABLE) ):
        #check if frame has content
        if len( FRAME_TABLE[frame] ) > 0:
            #if CPU_pid match
            if CPU_pid == FRAME_TABLE[frame]['PID']:
                #if page# match
                if page_num == FRAME_TABLE[frame]['PAGE']:
                    #update TIMESTAMP
                    FRAME_TABLE[frame]['TIMESTAMP'] = TIMESTAMP
                    #raise flag, match found
                    match = 1
                #end if
            #end if
        #end if
    #end for
    #if match wasnt found, create a new entry in FRAME_TABLE
    if match == 0:
        #if FRAME_TABLE is full, use LRU
        if pages_left == 0:
            #create a variable to store the index of the lRU Frame
            # - default, intialize to index of frame 0
            LRU_index = 0
            #create a variable to store the timestamp of the LRU frame
            # - default, initialize to TS of frame 0
            LRU_ts = FRAME_TABLE[0]['TIMESTAMP']
            #go thru every frame in FRAME_TABLE
            for frame in range( len( FRAME_TABLE) ):
                #store timestamp of current frame
                curr_ts = FRAME_TABLE[frame]['TIMESTAMP']
                #if curr_ts is smaller
                if curr_ts < LRU_ts:
                    #update LRU_ts
                    LRU_ts = curr_ts
                    #store index of LRU frame
                    LRU_index = frame
                #end if
            #end for
            #replace frame @ LRU_index w/ new process info
            FRAME_TABLE[LRU_index] = {'PAGE' : page_num, 'PID' : CPU_pid, 'TIMESTAMP' : TIMESTAMP}
        #else place at empty frame
        else:
            #decrement pages left
            pages_left -= 1
            #go thru FRAME_TABLE, look for empty frame
            for frame in range(len(FRAME_TABLE)):
                #if the len of the frame == 0
                if len(FRAME_TABLE[frame]) == 0:
                    #empty frame found, insert data here
                    FRAME_TABLE[frame] = {'PAGE' : page_num, 'PID' : CPU_pid, 'TIMESTAMP' : TIMESTAMP}
                    break
                #end if
            #end for
        #end if/else
    #end if match not found
    return pages_left
#end mem_access
# ****************************************************************

# ****************************************************************
# ****************************************************************
# ****************************************************************

#>>> setup
#receive user_cmd
print '********************************'
print '>>> BEGINNING SIMULATION'
RAM_SIZE = raw_input('Please input RAM size       : ')
PAGE_SIZE = raw_input('Please input page size      : ')
RAM_SIZE = int(RAM_SIZE)
PAGE_SIZE = int(PAGE_SIZE)
NUM_OF_PAGES = RAM_SIZE / PAGE_SIZE
NUM_OF_HDD = raw_input('Please input number of HDD  : ')
NUM_OF_HDD = int(NUM_OF_HDD)

#create a frame table
FRAME_TABLE = {}
for x in range(NUM_OF_PAGES):
    #make an empty frame for each page
    FRAME_TABLE[x] = {}
#initialize PID, TIMESTAMP, and pages_left
PID = 1
TIMESTAMP = 1
pages_left = NUM_OF_PAGES

#create a HDD table
HDD_table = {}
for x in range(NUM_OF_HDD):
    #make empty queues for each hard_drive
    HDD_table[x] = { 'PID':[], 'PRIORITY': [], 'FILENAME':[] }

#create and initialize CPU_pid, CPU_priority, and CPU_queue
CPU_pid = 0
CPU_priority = 0
CPU_queue = {}

#error statement
err_ = 'ERROR: Invalid User Command'

'''
#show state of the system
show_CPU(CPU_pid, CPU_priority, CPU_queue)
show_HDD(HDD_table)
show_mem(FRAME_TABLE)
#'''

print
print '@NOTE    INFO IS DISPLAYED AS [PID : PRIORITY] PAIRS'
print
#active portion of OS simulation
while(True):
    user_cmd = raw_input('Please enter your commad now: ')
    #turns empty user_cmd into 'none'
    if user_cmd == '':
        user_cmd = 'none'
    #split user command into a list
    parsed_cmd = user_cmd.split()
    #to check if a string is still valid after error checking
    valid = 1
    #read the first letter, choose function
    #new process
    if user_cmd[0] == 'A':
        #if there arent 2 words
        if len(parsed_cmd) != 2:
            print err_
            valid = 0
        #if there are 2 words
        if len(parsed_cmd) == 2:
            #and the 2nd word isnt an int
            try:
                decimal = int(parsed_cmd[1])
            except ValueError:
                print err_
                valid  = 0
        #if valid:
        if valid == 1:
            pages_left, CPU_pid, CPU_priority = new_process(user_cmd, PID, TIMESTAMP, FRAME_TABLE, pages_left, CPU_pid, CPU_priority, CPU_queue)
            PID += 1
            TIMESTAMP += 1
    #terminate
    elif user_cmd[0] == 't':
        #make sure there is only 1 word
        if len(parsed_cmd) != 1:
            print err_
            valid = 0
        #if valid
        if valid == 1:
            CPU_pid, CPU_priority, pages_left = terminate(CPU_pid, CPU_priority, CPU_queue, FRAME_TABLE, NUM_OF_PAGES, pages_left)
            TIMESTAMP += 1
    #disk access
    elif user_cmd[0] == 'd':
        #check for 3 elements
        if len(parsed_cmd) != 3:
            print err_
            valid = 0
        #if there are 3 elements
        else:
            #second element should be a number
            try:
                decimal = int(parsed_cmd[1])
            except ValueError:
                print err_
                valid = 0
            #end try
        #end if/else
        #if valid
        if valid == 1:
            #make sure disk exists
            if int(parsed_cmd[1]) > NUM_OF_HDD:
                print err_
                valid = 0
        #if valid
        if valid == 1:
            CPU_pid, CPU_priority = disk_access(user_cmd, CPU_pid, CPU_priority, CPU_queue, HDD_table)
    #disk complete
    elif user_cmd[0] == 'D':
        #check for 2 elements
        if len(parsed_cmd) != 2:
            print err_
            valid = 0
        #else if 2 elements
        else:
            #2nd element should be a num
            try:
                decimal = int(parsed_cmd[1])
            except ValueError:
                print err_
                valid = 0
            #end try
        #end if/else
        #if valid
        if valid == 1:
            #make sure disk # exists
            if int(parsed_cmd[1]) >= NUM_OF_HDD:
                print err_
                valid = 0
        #if valid
        if valid == 1:
            CPU_pid, CPU_priority = disk_complete(user_cmd, HDD_table, CPU_pid, CPU_priority, CPU_queue)
    #show all
    elif user_cmd == 'show':
        show_CPU(CPU_pid, CPU_priority, CPU_queue)
        show_HDD(HDD_table)
        show_mem(FRAME_TABLE)
    #show indivual component
    elif user_cmd[0] == 'S':
        #show CPU
        if user_cmd[2] == 'r':
            show_CPU(CPU_pid, CPU_priority, CPU_queue)
        #show HDD table
        elif user_cmd[2] == 'i':
            show_HDD(HDD_table)
        #show FRAME_TABLE
        elif user_cmd[2] == 'm':
            show_mem(FRAME_TABLE)
        else:
            print err_
    #mem access
    elif user_cmd[0] == 'm':
        #check for 2 elements
        if len(parsed_cmd) != 2:
            print err_
            valid = 0
        #if valid
        if valid == 1:
            pages_left = mem_acces (user_cmd, PAGE_SIZE, CPU_pid, FRAME_TABLE, pages_left, TIMESTAMP)
            TIMESTAMP += 1
    else:
        print err_
    print '---- ---- ---- ---- ---- ---- ---- ----'
    print
#end of while
print '>>> TERMINATING SIMULATION'
print '********************************'
