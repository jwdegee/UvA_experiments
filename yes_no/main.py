import sys
from session import PRSession
import appnope


def main():
    subject_initials = sys.argv[1]
    index_number = sys.argv[2]
    tracker_on = False
	    
    appnope.nope()

    ts = PRSession(subject_initials=subject_initials, index_number=index_number, tracker_on=tracker_on)
    

    ts.run()

if __name__ == '__main__':
    main()
