from unittest.mock import DEFAULT, patch


class PatcherBase:
    def add_patcher(self, target, new=DEFAULT, new_callable=None):
        target_patch = patch(target, new, new_callable)
        self.addCleanup(target_patch.stop)
        return target_patch.start()
