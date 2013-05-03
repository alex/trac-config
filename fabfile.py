from fabric.api import run, settings

from braid import pip, postgres, cron, git
from braid.twisted import service

from braid import config
_hush_pyflakes = [config]


class Trac(service.Service):
    def task_install(self):
        """
        Install trac.
        """
        self.bootstrap(python='system')

        # FIXME: Make these idempotent.
        postgres.createUser('trac')
        postgres.createDb('trac', 'trac')

        with settings(user=self.serviceUser):
            p = 'Genshi>=0.5 textile>=2.0 Pygments>=0.6 docutils>=0.3'.split()
            p = [ "'%s'" % a for a in p]
            pip.install(" ".join(p), python='system')
            self.task_update(_installDeps=True)

            run('mkdir ~/svn')
            run('ln -nsf ~/svn {}/trac-env/svn-repo'.format(self.configDir))

            run('mkdir ~/attachments')
            run('ln -nsf ~/svn {}/trac-env/attachments'.format(self.configDir))

            run('ln -nsf {} {}/trac-env/log'.format(self.logDir, self.configDir))

            run('ln -nsf {}/start {}/start'.format(self.configDir, self.binDir))

            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))


    def task_update(self, _installDeps=False):
        """
        Update trac config.
        """
        # TODO
        with settings(user=self.serviceUser):
            git.branch('https://github.com/twisted-infra/trac-config', self.configDir)
            git.branch('https://github.com/twisted-infra/twisted-trac-source.git', '.local/lib/python2.7/site-packages/trac')

globals().update(Trac('trac').getTasks())
