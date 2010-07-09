#
# Copyright (c) 2010 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#

from pulptools import *
from pulptools.agent import *
from pulptools.agent.remote import *
from pulptools.agent.action import *
from pulptools.config import Config
from pulptools.logutil import getLogger
from pmf.base import Agent as Base
from pmf.consumer import RequestConsumer
from time import sleep
from threading import Thread

log = getLogger(__name__)
cfg = Config()


class ActionThread(Thread):
    """
    Run actions independantly of main thread.
    @ivar actions: A list of actions to run.
    @type actions: [L{Action},..]
    """
    
    def __init__(self, actions):
        """
        @param actions: A list of actions to run.
        @type actions: [L{Action},..]
        """
        self.actions = actions
        Thread.__init__(self, name='Actions')
   
    def run(self):
        """
        Run actions.
        """
        while True:
            for action in self.actions:
                action()
            sleep(10)
            

class Agent(Base):
    """
    Pulp agent.
    """
    def __init__(self, actions=[]):
        id = self.id()
        actionThread = ActionThread(actions)
        actionThread.start()
        host = cfg.pmf.host
        port = int(cfg.pmf.port)
        consumer = RequestConsumer(id, host, port)
        Base.__init__(self, consumer)
        log.info('%s - started.', id)
        actionThread.join()

    def id(self):
        """
        Get agent id.
        @return: The agent UUID.
        """
        cid = ConsumerId()
        while ( not cid.uuid ):
            log.info('Not registered.')
            sleep(60)
            cid.read()
        return cid.uuid


def main():
    """
    Agent main.
    Add recurring, time-based actions here.
    All actions must be subclass of L{action.Action}.
    """
    actions = \
     (TestAction(minutes=1),
      ProfileUpdateAction(minutes=cfg.server.interval),
      # <add actions here>
      )
    agent = Agent(actions)
    agent.close()


if __name__ == '__main__':
    main()
