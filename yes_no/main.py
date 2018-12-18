import os, sys
from session import PRSession
import appnope

from analyse_main import analyse_yesno

def main():

    subject_initials = str(raw_input('Your initials: '))
    index_number = int(raw_input('Which run: '))
    version_number = int(raw_input('Version: ') )

    tracker_on = False
    screen_params = {'size':(800,600), 'full_screen': False}

    appnope.nope()

    ts = PRSession(subject_initials=subject_initials, index_number=index_number, tracker_on=tracker_on, **screen_params)
    ts.run()

    # autmatically move files:
    if not os.path.exists('data/decision/{}/'.format(subject_initials)):
        os.makedirs('data/decision/{}/'.format(subject_initials))
    os.system('mv %s %s' % (ts.output_file + '.edf', 'data/decision/' + subject_initials + '/' + os.path.split(ts.output_file)[1] + '.edf'))
    os.system('mv %s %s' % (ts.output_file + '.tsv', 'data/decision/' + subject_initials + '/' + os.path.split(ts.output_file)[1] + '.tsv'))
    os.system('mv %s %s' % (ts.output_file + '_outputDict.pkl', 'data/decision/' + subject_initials + '/' + os.path.split(ts.output_file)[1] + '_outputDict.pkl'))

    # run behavioural analysis:
    analyse_yesno(filename='data/decision/' + subject_initials + '/' + os.path.split(ts.output_file)[1] + '.tsv')

if __name__ == '__main__':
    main()
