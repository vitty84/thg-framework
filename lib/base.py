import argparse
import time
import threading
from queue import Queue
from lib.cmd2 import Cmd, with_category, with_argparser
from art import text2art, art
from utils import module
from pathlib import Path
from colorama import Fore, Style
from tabulate import tabulate
import platform
from colorama import Fore
from config.Version import __codenome__,__version__
from config.info_init import *
from importlib import import_module, reload
from lib.Database import Database
from lib.BaseOption import ExploitOption
from lib.exception.Module import ModuleNotUseException


class THGBASECONSOLE(Cmd, Database):
    colors = "Always"

    console_prompt = "{COLOR_START}thg-console{COLOR_END}".format(COLOR_START=Fore.CYAN, COLOR_END=Fore.BLUE)
    console_prompt_end = " > "
    module_name = None
    module_class = None
    module_instance = None

    # command categories
    CMD_CORE = "Core Command"
    CMD_MODULE = "Module Command"

    def __init__(self):
        super(THGBASECONSOLE, self).__init__()
        Database.__init__(self)
        self.prompt = self.console_prompt + self.console_prompt_end
        self.do_banner(None)

    @with_category(CMD_CORE)
    def do_banner(self, args):
        # exploits_count=self.modules_count["exploits"] + self.modules_count['extra_exploits'],
        # encoders_count=self.modules_count["encoders"] + self.modules_count['extra_encoders'],
        # auxiliary_count=self.modules_count["auxiliary"] + self.modules_count['extra_auxiliary'],
        # nops_count=self.modules_count["nops"] + self.modules_count['extra_nops'],
        # payloads_count=self.modules_count["payloads"] + self.modules_count['extra_payloads'],
        # post_count=self.modules_count["post"] + self.modules_count['extra_post'],
        #                    evasion_count=self.modules_count["evasion"],
        """Print thg-console banner"""
        ascii_text = text2art("thg-console", "rand")
        self.poutput("\n\n")
        self.poutput(ascii_text, '\n\n', color=Fore.LIGHTCYAN_EX)
        #self.poutput("thg-console has {count} modules".format(count=self.get_module_count()), "\n\n", color=Fore.MAGENTA)
        self.banner = """
        {CYAN}==================={GREEN}[ thgconsole {version} ]{GREEN}{CYAN}===================

        {YELLOW}+ -- --=[{RED}THGEF   :{MAGENTA} The Hacker Group Exploitation Framework{RED}{YELLOW}]=-- -- +    
        {YELLOW}+ -- --=[{RED}Code by :{MAGENTA} Darkcode                               {RED}{YELLOW}]=-- -- + 
        {YELLOW}+ -- --=[{RED}Codename:{MAGENTA} {codenome}                                {RED}{YELLOW}]=-- -- + 
        {YELLOW}+ -- --=[{RED}Homepage:{MAGENTA} https://www.facebook.com/darckode0x00/ {RED}{YELLOW}]=-- -- + 
        {YELLOW}+ -- --=[{RED}youtube :{MAGENTA} darkcode programming                   {RED}{YELLOW}]=-- -- + 

        {CYAN}==================={GREEN}[ thgconsole-pc ]{GREEN}{CYAN}========================

        {YELLOW}+ -- --=[{RED}system  =>{MAGENTA} {os}             {RED}{YELLOW}]=-- -- + 
        {YELLOW}+ -- --=[{RED}machine =>{MAGENTA} {machine}            {RED}{YELLOW}]=-- -- +      
        {YELLOW}+ -- --=[{RED}gcc     =>{MAGENTA} {gccv}             {RED}{YELLOW}]=-- -- +
        {YELLOW}+ -- --=[{RED}python  =>{MAGENTA} {python}               {RED}{YELLOW}]=-- -- +
        {YELLOW}+ -- --=[{RED}net     =>{MAGENTA} {net}        {RED}{YELLOW}]=-- -- +
        {YELLOW}+ -- --=[{RED}ip      =>{MAGENTA} {ip}       {RED}{YELLOW}]=-- -- +
        {YELLOW}+ -- --=[{RED}mac     =>{MAGENTA} {mac} {RED}{YELLOW}]=-- -- +

        {CYAN}==================={GREEN}[ thgconsole-info ]{GREEN}{CYAN}========================
        {CYAN}==================={GREEN}[ thgconsole-config ]{GREEN}{CYAN}========================
        {YELLOW}+ -- --=[{RED}DB_STATUS =>{MAGENTA}off next fix 2.0.4  {RED}{YELLOW}]=-- -- +
                """.format(os=platform.uname()[0],
                           release=platform.uname()[2],
                           versao=platform.uname()[3],
                           machine=platform.uname()[4],
                           processor=platform.uname()[5],
                           hostname=platform.uname()[1],
                           codenome=__codenome__,
                           version=__version__,
                           CYAN=Fore.CYAN,
                           GREEN=Fore.GREEN,
                           RED=Fore.RED,
                           YELLOW=Fore.YELLOW,
                           MAGENTA=Fore.MAGENTA,
                           gccv=thg_add_init.check_gcc_version(),
                           python=thg_add_init.check_python_version(),
                           net=thg_add_init.is_connected(),
                           ip=thg_add_init.ipi(),
                           mac=thg_add_init.get_mac())
        print(self.banner)

    @with_category(CMD_MODULE)
    def do_listmod(self, args):
        """List all modules"""
        local_modules = module.get_local_modules()
        self._print_modules(local_modules, "Module List:")

    @with_category(CMD_MODULE)
    def do_search(self, args):
        """
        Search modules

        Support fields:
            name, module_name, description, author, disclosure_date, service_name, service_version, check
        Eg:
            search redis
            search service_name=phpcms  service_version=9.6.0
        """
        search_conditions = args.split(" ")
        db_conditions = {}
        for condition in search_conditions:
            cd = condition.split("=")
            if len(cd) is 1:
                [module_name] = cd
                db_conditions['module_name'] = module_name
            else:
                [field, value] = cd
                if field in self.searchable_fields:
                    db_conditions[field] = value

        modules = self.search_modules(db_conditions)

        self._print_modules(modules, 'Search results:')
        self._print_item("search mod => name, module_name, description, author, disclosure_date, service_name, service_version, check")
        self._print_item("The search is only retrieved from the database")
        self._print_item("If you add/delete some new modules, please execute `db_rebuild` first\n\n")

    def complete_set(self, text, line, begidx, endidx):
        if len(line.split(" ")) > 2:
            completion_items = []
        else:
            completion_items = ['debug']
            if self.module_instance:
                completion_items += [option.name for option in self.module_instance.options.get_options()]
        return self.basic_complete(text, line, begidx, endidx, completion_items)

    set_parser = argparse.ArgumentParser()
    set_parser.add_argument("name", help="The name of the field you want to set")
    set_parser.add_argument("-f", "--file", action="store_true", help="Specify multiple targets")
    set_parser.add_argument("value", help="The value of the field you want to set")

    @with_argparser(set_parser)
    @with_category(CMD_MODULE)
    def do_set(self, args):
        """Set module option value/ set program config"""
        if args.name == 'debug':
            self.debug = args.value
            return None

        if not self.module_instance:
            raise ModuleNotUseException()
        if args.file and args.name in ["HOST", "URL"]:
            try:
                open(args.value, 'r')
                self.module_instance.multi_target = True
            except IOError as e:
                self._print_item(e, color=Fore.RED)
                return False
        elif not args.file and args.name in ["HOST", "URL"]:
            self.module_instance.multi_target = False
            self.module_instance.targets = None

        self.module_instance.options.set_option(args.name, args.value)

    def complete_use(self, text, line, begidx, endidx):
        if len(line.split(" ")) > 2:
            modules = []
        else:
            modules = [local_module[0] for local_module in module.get_local_modules()]
        return self.basic_complete(text, line, begidx, endidx, modules)

    @with_category(CMD_MODULE)
    def do_use(self, module_name, module_reload=False):
        """Chose a module"""
        module_file = module.name_convert(module_name)
        module_type = module_name.split("/")[0]

        if Path(module_file).is_file():
            self.module_name = module_name
            if module_reload:
                self.module_class = reload(self.module_class)
            else:
                self.module_class = import_module("modules.{module_name}".format(module_name=module_name.replace("/", ".")))
            self.module_instance = self.module_class.Exploit()
            self.set_prompt(module_type=module_type, module_name=module_name)
        else:
            self.poutput("Module/Exploit not found.")

    @with_category(CMD_MODULE)
    def do_back(self, args):
        """Clear module that chose"""
        self.module_name = None
        self.module_instance = None
        self.prompt = self.console_prompt + self.console_prompt_end

    def complete_show(self, text, line, begidx, endidx):
        if len(line.split(" ")) > 2:
            completion_items = []
        else:
            completion_items = ['info', 'options', 'missing']
        return self.basic_complete(text, line, begidx, endidx, completion_items)

    @with_category(CMD_MODULE)
    def do_show(self, content):
        """
        Display module information

        Eg:
            show info
            show options
            show missing
        """
        if not self.module_instance:
            raise ModuleNotUseException()

        if content == "info":
            info = self.module_instance.get_info()
            info_table = []
            self.poutput("Module info:", "\n\n", color=Fore.CYAN)
            for item in info.keys():
                info_table.append([item + ":", info.get(item)])
            self.poutput(tabulate(info_table, colalign=("right",), tablefmt="plain"), "\n\n")

        if content == "options" or content == "info":
            options = self.module_instance.options.get_options()
            default_options_instance = ExploitOption()
            options_table = []
            for option in options:
                options_table_row = []
                for field in default_options_instance.__dict__.keys():
                    options_table_row.append(getattr(option, field))
                options_table.append(options_table_row)

            self.poutput("Module options:", "\n\n", color=Fore.CYAN)
            self.poutput(
                tabulate(
                    options_table,
                    headers=default_options_instance.__dict__.keys(),
                ),
                "\n\n"
            )

        if content == "missing":
            missing_options = self.module_instance.get_missing_options()
            if len(missing_options) is 0:
                self.poutput("No option missing!", color=Fore.CYAN)
                return None

            default_options_instance = ExploitOption()
            missing_options_table = []
            for option in missing_options:
                options_table_row = []
                for field in default_options_instance.__dict__.keys():
                    options_table_row.append(getattr(option, field))
                missing_options_table.append(options_table_row)
            self.poutput("Missing Module options:", "\n\n", color=Fore.CYAN)
            self.poutput(
                tabulate(
                    missing_options_table,
                    headers=default_options_instance.__dict__.keys(),
                ),
                "\n\n"
            )

    @with_category(CMD_MODULE)
    def do_run(self, args):
        """alias to exploit"""
        self.do_exploit(args=args)

    def exploit_thread(self, target, target_type, thread_queue):
        target_field = None
        port = None

        if target_type == "tcp":
            [target, port] = module.parse_ip_port(target)
            target_field = "HOST"
        elif target_type == "http":
            target_field = "URL"
        exp = self.module_class.Exploit()
        exp.options.set_option(target_field, target)
        exp.options.set_option("TIMEOUT", self.module_instance.options.get_option("TIMEOUT"))
        if port:
            exp.options.set_option("PORT", port)
        else:
            exp.options.set_option("PORT", self.module_instance.options.get_option("PORT"))

        exploit_result = exp.exploit()

        if exploit_result.status:
            self._print_item(exploit_result.success_message)
        else:
            self._print_item(exploit_result.error_message, color=Fore.RED)
        thread_queue.get(1)

    @with_category(CMD_MODULE)
    def do_exploit(self, args):
        """Execute module exploit"""
        if not self.module_instance:
            raise ModuleNotUseException()

        [validate_result, validate_message] = self.module_instance.options.validate()
        if not validate_result:
            for error in validate_message:
                self._print_item(error, color=Fore.RED)
            return False


        if self.module_instance.multi_target:

            target_type = self.module_instance.target_type
            target_field = None

            if target_type == "tcp":
                target_field = "HOST"
            elif target_type == "http":
                target_field = "URL"

            target_filename = self.module_instance.options.get_option(target_field)

            try:
                target_file = open(target_filename, 'r')
                self.module_instance.targets = []
                for line in target_file.readlines():
                    self.module_instance.targets.append(line.strip())
                self.module_instance.multi_target = True
            except IOError as e:
                self._print_item(e, color=Fore.RED)
                return False


            targets = self.module_instance.targets
            targets_queue = Queue()
            for target in targets:
                targets_queue.put(target)


            if not targets_queue.empty():
                thread_count = int(self.module_instance.options.get_option("THREADS"))
                thread_queue = Queue(maxsize=thread_count)

                try:
                    while not targets_queue.empty():
                        while thread_queue.full():
                            time.sleep(0.1)

                        target = targets_queue.get()
                        thread_queue.put(1)
                        _thread = threading.Thread(target=self.exploit_thread, args=(target, target_type, thread_queue))
                        _thread.start()

                    while not thread_queue.empty():
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    self._print_item("Wait for existing process to exit...", color=Fore.RED)
                    while threading.activeCount() > 1:
                        time.sleep(0.5)
                    return None

            self.poutput("{style}[*]{style_end} module execution completed".format(
                style=Fore.BLUE + Style.BRIGHT,
                style_end=Style.RESET_ALL
            ))
            return False

        exploit_result = self.module_instance.exploit()
        if exploit_result.status:
            self._print_item("Exploit success!")
            self._print_item(exploit_result.success_message)
        else:
            self._print_item("Exploit failure!", color=Fore.RED)
            self._print_item(exploit_result.error_message, color=Fore.RED)
        self.poutput("{style}[*]{style_end} module execution completed".format(
            style=Fore.BLUE + Style.BRIGHT,
            style_end=Style.RESET_ALL
        ))

    def check_thread(self, target, target_type, thread_queue):
        target_field = None
        port = None

        if target_type == "tcp":
            [target, port] = module.parse_ip_port(target)
            target_field = "HOST"
        elif target_type == "http":
            target_field = "URL"
        exp = self.module_class.Exploit()
        exp.options.set_option(target_field, target)
        exp.options.set_option("TIMEOUT", self.module_instance.options.get_option("TIMEOUT"))
        if port:
            exp.options.set_option("PORT", port)
        else:
            exp.options.set_option("PORT", self.module_instance.options.get_option("PORT"))

        exploit_result = exp.check()

        if exploit_result.status:
            self._print_item(exploit_result.success_message)
        else:
            self._print_item(exploit_result.error_message, color=Fore.RED)
        thread_queue.get(1)

    @with_category(CMD_MODULE)
    def do_check(self, args):
        """Execute module check"""
        if not self.module_instance:
            raise ModuleNotUseException()

        [validate_result, validate_message] = self.module_instance.options.validate()
        if not validate_result:
            for error in validate_message:
                self._print_item(error, Fore.RED)
            return False

        # 处理指定多个目标的情况
        if self.module_instance.multi_target:
            # 读取多个目标
            target_type = self.module_instance.target_type
            target_field = None

            if target_type == "tcp":
                target_field = "HOST"
            elif target_type == "http":
                target_field = "URL"

            target_filename = self.module_instance.options.get_option(target_field)

            try:
                target_file = open(target_filename, 'r')
                self.module_instance.targets = []
                for line in target_file.readlines():
                    self.module_instance.targets.append(line.strip())
                self.module_instance.multi_target = True
            except IOError as e:
                self._print_item(e, color=Fore.RED)
                return False

            targets = self.module_instance.targets
            targets_queue = Queue()
            for target in targets:
                targets_queue.put(target)

            if not targets_queue.empty():
                thread_count = int(self.module_instance.options.get_option("THREADS"))
                thread_queue = Queue(maxsize=thread_count)

                try:
                    while not targets_queue.empty():
                        while thread_queue.full():
                            time.sleep(0.1)

                        target = targets_queue.get()
                        thread_queue.put(1)
                        _thread = threading.Thread(target=self.check_thread,
                                                   args=(target, target_type, thread_queue))
                        _thread.start()

                    while not thread_queue.empty():
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    self._print_item("Wait for existing process to exit...", color=Fore.RED)
                    while threading.activeCount() > 1:
                        time.sleep(0.5)
                    return None

            self.poutput("{style}[*]{style_end} module execution completed".format(
                style=Fore.BLUE + Style.BRIGHT,
                style_end=Style.RESET_ALL
            ))
            return None

        exploit_result = self.module_instance.check()

        if exploit_result is None:
            self._print_item("Check Error: check function no results returned")
            return None

        if exploit_result.status:
            self._print_item("Check success!")
            self._print_item(exploit_result.success_message)
        else:
            self._print_item("Exploit failure!", color=Fore.RED)
            self._print_item(exploit_result.error_message, color=Fore.RED)
        self.poutput("{style}[*]{style_end} module execution completed".format(
            style=Fore.BLUE + Style.BRIGHT,
            style_end=Style.RESET_ALL
        ))

    @with_category(CMD_CORE)
    def do_db_rebuild(self, args):
        """Rebuild database for search"""
        self.db_rebuild()
        self.poutput("Database rebuild done.", color=Fore.GREEN)

    @with_category(CMD_MODULE)
    def do_reload(self, args):
        """reload the chose module"""
        self.do_use(self.module_name, module_reload=True)

    def set_prompt(self, module_type, module_name):
        module_prompt = " {module_type}({color}{module_name}{color_end})".format(
            module_type=module_type,
            module_name=module_name.replace(module_type + "/", ""),
            color=Fore.RED,
            color_end=Fore.RESET
        )
        self.prompt = self.console_prompt + module_prompt + self.console_prompt_end

    def _print_modules(self, modules, title):
        self.poutput(title, "\n\n", color=Fore.CYAN)
        self.poutput(tabulate(modules, headers=('module_name', 'check', 'disclosure_date', 'description')), '\n\n')

    def _print_item(self, message, color=Fore.YELLOW):
        self.poutput("{style}[+]{style_end} {message}".format(
            style=color + Style.BRIGHT,
            style_end=Style.RESET_ALL,
            message=message,
        ))
