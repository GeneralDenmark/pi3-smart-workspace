from i3ipc import Connection
import sys
from pprint import pprint
import pynput
import re
import argparse


class WorkSpacer:

    def __init__(self, index):
        self.i3 = None
        self.index = index
        self.workspaces_on_outputs = {}
        self.workspaces = None
        self.outputs = None
        self.config = None
        self.mouse = pynput.mouse.Controller()
        self.mouse_position = None
        self.current_output_name = None

    def _connect(self):
        try:
            self.i3 = Connection()
            self.config = self.i3.get_config().__dict__['config']
            config_outputs = {}
            for matchNo, match in enumerate(
                    re.finditer(r'set (\$[a-zA-Z]+) ((HDMI|DP|VGA)-\d)', self.config, re.MULTILINE), start=1
            ):
                config_outputs[match.group(1)] = match.group(2)
            pprint(config_outputs)
            config_workspace_names = {}
            for matchNum, match in enumerate(
                re.finditer(r'set (\$.*) (\d.*)', self.config, re.MULTILINE)
            ):
                config_workspace_names[match.group(1)] = match.group(2)
            pprint(config_workspace_names)
            for matchNum, match in enumerate(
                re.finditer(r'workspace (\$.*) output (\$.*)', self.config, re.MULTILINE)
            ):
                if not self.workspaces_on_outputs.keys().__contains__(config_outputs[match.group(2)]):
                    self.workspaces_on_outputs[config_outputs[match.group(2)]] = []
                self.workspaces_on_outputs[config_outputs[match.group(2)]].append(config_workspace_names[match.group(1)])

        except Exception as exc:
            sys.exit(1)
        self.workspaces = [workspaces for workspaces in  self.i3.get_workspaces()]
        outputs = self.i3.get_outputs()
        self.outputs = [output for output in outputs if output.__dict__["active"] is True]

    def run(self):
        self._connect()
        self.mouse_position = self.mouse.position
        self.current_output_name = self._get_workspace_from_courser_position()
        self.i3.command(f'workspace {self.workspaces_on_outputs[self.current_output_name][self.index]}')

    def _get_workspace_from_courser_position(self):
        for output in self.outputs:
            width = output.__dict__["rect"].__dict__["width"]
            height = output.__dict__["rect"].__dict__["height"]
            x_offset = output.__dict__["rect"].__dict__["x"]
            y_offset = output.__dict__["rect"].__dict__["y"]

            if x_offset == 0 and y_offset == 0:
                if x_offset <= self.mouse_position[0] <= x_offset + width and y_offset <= self.mouse_position[1] <= y_offset + height:
                    return output.__dict__["name"]
            elif x_offset == 0:
                if x_offset <= self.mouse_position[0] <= x_offset + width and y_offset < self.mouse_position[1] <= y_offset + height:
                    return output.__dict__["name"]
            elif y_offset == 0:
                if x_offset < self.mouse_position[0] <= x_offset + width and y_offset <= self.mouse_position[1] <= y_offset + height:
                    return output.__dict__["name"]
            else:
                if x_offset < self.mouse_position[0] <= x_offset + width and y_offset < self.mouse_position[1] <= y_offset + height:
                    return output.__dict__["name"]

    def _get_workspaces_for_output(self, output):
        return [workspace for workspace in self.workspaces if workspace.__dict__['output'] == output]


def main():
    parser = argparse.ArgumentParser(
        description="Dynamic changes the workspace, based on what output your cursoer is on."
    )
    parser.add_argument("-i", "--index", type=int,
                        help="the number index of the workspace that should be openend. 1 =  first workspace in config etc.")
    ws = WorkSpacer(parser.parse_args().index - 1)
    ws.run()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


