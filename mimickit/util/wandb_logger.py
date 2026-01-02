import os

try:
    import wandb
except ImportError:
    wandb = None

import util.logger as logger


class WandbLogger(logger.Logger):
    MISC_TAG = "Misc"

    def __init__(self, project_name, param_config):
        super().__init__()

        self._project_name = project_name
        self._param_config = param_config
        self._step_key = None
        self._collections = dict()

    def reset(self):
        super().reset()

    def configure_output_file(self, filename=None):
        super().configure_output_file(filename)

        # Only initialize wandb if available and we are root logger
        if wandb is not None and logger.Logger.is_root():
            basename = os.path.basename(filename)
            exp_name = os.path.splitext(basename)[0]
            wandb.init(
                project=self._project_name,
                name=exp_name,
                config=self._param_config
            )

    def set_step_key(self, var_key):
        self._step_key = var_key

    def log(self, key, val, collection=None, quiet=False):
        super().log(key, val, quiet)

        if collection is not None:
            self._add_collection(collection, key)

    def write_log(self):
        row_count = self._row_count
        super().write_log()

        # Safely skip wandb logging if unavailable
        if wandb is None or not logger.Logger.is_root() or wandb.run is None:
            return

        if row_count == 0:
            self._key_tags = self._build_key_tags()

        step_val = row_count
        if self._step_key is not None:
            step_val = self.log_current_row.get(self._step_key, "").val

        out_dict = dict()
        for i, key in enumerate(self.log_headers):
            if key != self._step_key:
                entry = self.log_current_row.get(key, "")
                out_dict[self._key_tags[i]] = entry.val

        wandb.log(out_dict, step=int(step_val))

    def _add_collection(self, name, key):
        if name not in self._collections:
            self._collections[name] = []
        self._collections[name].append(key)

    def _build_key_tags(self):
        tags = []
        for key in self.log_headers:
            curr_tag = WandbLogger.MISC_TAG
            for col_tag, col_keys in self._collections.items():
                if key in col_keys:
                    curr_tag = col_tag
            tags.append(f"{curr_tag}/{key}")
        return tags

