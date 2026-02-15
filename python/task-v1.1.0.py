from datetime import datetime
from tkinter import messagebox, simpledialog, ttk
import json
import os
import tkinter as tk
import tkinter.filedialog as filedialog

class Task:
    def __init__(self, app, master):
        #【分頁1功能框架創立】
        self.groups = ["無"]  # 初始化群組列表
        self.all_tasks = []
        self.tasks = [] # 用於儲存當前篩選後的任務
        self.current_filter = {"priority": None, "group": None, "status": None} # 新增篩選條件儲存

        self.app = app
        self.page1 = master # 將傳遞進來的 master 賦值給 self.page1

        # 創建 Treeview 的樣式
        self.style = ttk.Style(master) # 使用 RightPanel 的 master
        self.style.theme_use("default")
        self._configure_treeview_style() # 初始化 Treeview 樣式

        self.original_order = []
        self.sort_order = True
        self.sort_option = tk.StringVar(value="添加時間")

        self.load_groups_from_json() # 先載入群組資料
        self.create_task_manager_content(self.page1) # 然後創建 UI，包含 treeview
        self.load_tasks_from_json() # 最後載入任務資料，此時 treeview 應該已存在

        # 初始化 Treeview 標題的標籤 (確保在 treeview 創建後進行)
        self.treeview_heading_tags = {
            "priority": "priority_header",
            "group": "group_header",
            "status": "status_header"
        }
        # 注意：這裡不進行 tag_configure，而是在 create_task_manager_content 中進行

    def load_groups_from_json(self):
        try:
            filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", "tasks.json")
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.groups = data.get("groups", ["無"])
        except json.JSONDecodeError:
            print("警告：tasks.json 檔案格式錯誤。")
        except Exception as e:
            pass
                
    # 框架建立相關函數
    def _configure_treeview_style(self, priority_bg=None, group_bg=None, status_bg=None):
        """配置 Treeview 的樣式，允許動態設定標題背景色"""
        default_bg = "#d9d9d9" # 預設標題背景色

        self.style.configure("Treeview.Heading",
                             background=default_bg,
                             foreground="#000000",
                             borderwidth=0,
                             relief="flat",
                             font=("Arial", 10))

        if priority_bg:
            self.style.configure("Priority.Treeheading", background=priority_bg)
        else:
            self.style.configure("Priority.Treeheading", background=default_bg)

        if group_bg:
            self.style.configure("Group.Treeheading", background=group_bg)
        else:
            self.style.configure("Group.Treeheading", background=default_bg)

        if status_bg:
            self.style.configure("Status.Treeheading", background=status_bg)
        else:
            self.style.configure("Status.Treeheading", background=default_bg)

        self.style.configure("Treeview.Cell", borderwidth=0, relief="flat")
        self.style.map("Treeview",
                       background=[("selected", "#4a90e2")],
                       foreground=[("selected", "white")])    
    
    def create_task_manager_content(self, root):
            """創建任務管理視窗的內容"""
            self.root = root  # 將 page1 賦值給 self.root
            self.add_task_window_open = False

            self.original_order = []  # 新增原始添加順序列表

            self.tree_frame = tk.Frame(self.root)
            self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # 垂直滾動軸
            self.tree_scroll_y = tk.Scrollbar(self.tree_frame)
            self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

            # 水平滾動軸
            self.tree_scroll_x = tk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)
            self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

            self.treeview = ttk.Treeview(
                self.tree_frame,
                columns=("name", "priority", "deadline", "status", "group"),
                show="headings",
                yscrollcommand=self.tree_scroll_y.set,
                xscrollcommand=self.tree_scroll_x.set,
                style="Treeview",  # 套用樣式
            )

            # 移除關於標籤的定義和配置，因為 `-tags` 選項不被支援
            # self.treeview_heading_tags = {
            #     "priority": "priority_header",
            #     "group": "group_header",
            #     "status": "status_header"
            # }
            # self.treeview.tag_configure("priority_header", background="#d9d9d9") # 預設背景色
            # self.treeview.tag_configure("group_header", background="#d9d9d9") # 預設背景色
            # self.treeview.tag_configure("status_header", background="#d9d9d9") # 預設背景色

            self.treeview.heading("name", text="任務")
            self.treeview.heading("priority", anchor="center", text="優先級", command=lambda: self.filter_priority()) 
            self.treeview.heading("deadline", anchor="center", text="截止日", command=lambda: self.sort_deadline())
            self.treeview.heading("status", anchor="center", text="狀態", command=self.filter_status) 
            self.treeview.heading("group", anchor="center", text="群組", command=lambda: self.filter_group()) 

            # 設定欄位寬度
            self.treeview.column("name", width=200, stretch=False)
            self.treeview.column("priority", width=65, anchor="center", stretch=False)
            self.treeview.column("deadline", width=110, anchor="center", stretch=False)
            self.treeview.column("status", width=60, anchor="center", stretch=False)
            self.treeview.column("group", width=150, anchor="center", stretch=False)

            self.sort_order = True  # 預設排序方式為升序

            # 定義 "未動工" 狀態的標籤樣式，文字顏色為紅色。完成為綠色。暫停為藍色
            self.treeview.tag_configure("undone", foreground="red")
            self.treeview.tag_configure("completed", foreground="green")
            self.treeview.tag_configure("pause", foreground="blue")

            self.treeview.pack(fill=tk.BOTH, expand=True)

            # 設定滾動軸命令
            self.tree_scroll_y.config(command=self.treeview.yview)
            self.tree_scroll_x.config(command=self.treeview.xview)

            self.treeview.bind("<Button-3>", self.show_right_click_menu)
            self.treeview.bind("<ButtonRelease-1>", self.limit_column_widths)

            # 排序選項 (確保在載入前初始化)
            self.sort_option = tk.StringVar()
            self.sort_option.set("添加時間")  # 預設按添加時間排序

            # 載入 tasks.json 檔案並顯示任務
            self.load_tasks_from_json()

            # 排序單選按鈕
            self.sort_frame = tk.Frame(self.root, bg="#e8e8e8")  # 設定 Frame 的背景色
            self.sort_frame.pack(pady=10)

            self.update_time_radio = tk.Radiobutton(
                self.sort_frame,
                text="按更新時間排",
                variable=self.sort_option,
                value="更新時間",
                command=self.sort_tasks,
                bg="#e8e8e8",  # 設定與 Frame 相同的背景色
                highlightthickness=0,  # 移除高亮邊框
                bd=0,  # 移除普通邊框 (bd 是 borderwidth 的縮寫)
                state="disabled"  # 禁用按鈕
            )
            self.update_time_radio.pack(side=tk.LEFT)

            self.add_time_radio = tk.Radiobutton(
                self.sort_frame,
                text="按添加時間排",
                variable=self.sort_option,
                value="添加時間",
                command=self.sort_tasks,
                bg="#e8e8e8",  # 設定與 Frame 相同的背景色
                highlightthickness=0,  # 移除高亮邊框
                bd=0  # 移除普通邊框 (bd 是 borderwidth 的縮寫)
            )
            self.add_time_radio.pack(side=tk.LEFT)

            self.priority_radio = tk.Radiobutton(
                self.sort_frame,
                text="按優先級排",
                variable=self.sort_option,
                value="優先級",
                command=self.sort_tasks,
                bg="#e8e8e8",
                highlightthickness=0,
                bd=0
            )
            self.priority_radio.pack(side=tk.LEFT)

            self.deadline_radio = tk.Radiobutton(
                self.sort_frame,
                text="按截止時間排",
                variable=self.sort_option,
                value="截止時間",
                command=self.sort_tasks,
                bg="#e8e8e8",
                highlightthickness=0,
                bd=0
            )
            self.deadline_radio.pack(side=tk.LEFT)

            # 新增任務按鈕和例行任務按鈕
            self.add_button_frame = tk.Frame(self.root, bg="#e8e8e8")  # 設定 Frame 的背景色
            self.add_button_frame.pack(side=tk.BOTTOM, pady=10)

            self.add_button = tk.Button(self.add_button_frame, text="新增任務", command=self.open_add_task_window)
            self.add_button.pack(side=tk.LEFT, padx=5)

            self.routine_button = tk.Button(self.add_button_frame, text="例行任務", state=tk.DISABLED)  # 暫時禁用例行任務按鈕
            self.routine_button.pack(side=tk.LEFT, padx=5)
            
            self.output_task_button = tk.Button(self.add_button_frame, text="管理任務檔", command=self._open_merge_export_window)
            self.output_task_button.pack(side=tk.LEFT, padx=5)

            self.sort_tasks() # 在所有 UI 元素初始化完成後調用排序
    
    def tool_task(self):
        """打開任務管理視窗"""
        self.notebook.select(self.page1) #直接切換到任務管理分頁    
    
    def limit_column_widths(self, event=None):
        min_width = {
            "name": 65,
            "priority": 65,
            "deadline": 65,
            "status": 65,
            "group": 65,
        }
        max_width = {
            "name": 300,
            "priority": 100,
            "deadline": 150,
            "status": 80,
            "group": 250,
        }

        for col in self.treeview["columns"]:
            current_width = self.treeview.column(col)["width"]
            new_width = max(min_width[col], min(current_width, max_width[col]))
            if new_width != current_width:
                self.treeview.column(col, width=new_width)
    
    
    
    #-------------------------------------------------------------------------------------------------------------      
    # 資料處理 & 展示相關函數    
    def update_task_in_json(self, updated_task):
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", "tasks.json")
        try:
            with open(filename, "r+", encoding="utf-8") as f:
                data = json.load(f)
                tasks = data.get("tasks", [])
                found = False
                for item in tasks:
                    task_id_in_file = item.get("task", {}).get("id")
                    updated_task_id = updated_task.get("id")
                    if task_id_in_file == updated_task_id:
                        item["task"].update(updated_task) # 更新找到的任務
                        found = True
                        break
                if found:
                    f.seek(0)
                    json.dump(data, f, indent=4, ensure_ascii=False)
                    f.truncate()

        except FileNotFoundError:
            print("警告：tasks.json 檔案不存在。")
        except json.JSONDecodeError:
            print("警告：tasks.json 檔案格式錯誤。")
        except Exception as e:
            print(f"更新 tasks.json 時發生錯誤：{e}")    
    
    def remove_task_from_treeview(self, task_id):
        """從 Treeview 中移除指定 ID 的任務"""
        for item in self.treeview.get_children():
            if self.treeview.item(item, 'text') == task_id: # 使用 'text' 屬性來匹配 ID
                self.treeview.delete(item)
                break
        # 同時更新 self.tasks 列表，移除已完成的任務
        self.tasks = [task for task in self.tasks if task.get("id") != task_id]
        # 重新應用目前的篩選條件，以更新 Treeview 的顯示
        self.apply_filter()

    def remove_task_from_local_list(self, task_id_to_remove):
        """根據任務 ID 從本地 self.tasks 列表中移除任務"""
        original_len = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.get('id') != task_id_to_remove]
        if len(self.tasks) < original_len:
            print(f"任務 ID '{task_id_to_remove}' 已從本地列表移除。")
        else:
            print(f"警告：本地列表中找不到 ID 為 '{task_id_to_remove}' 的任務以進行移除。")
        self.apply_filter() # 移除後重新應用篩選
    
    def load_completed_tasks(self):
        """載入所有已完成的任務並顯示"""
        print("load_completed_tasks 函數被調用") # 添加調試資訊
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", "tasks.json")
        completed_tasks_from_file = []
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        all_tasks = [item["task"] for item in data.get("tasks", [])]
                    elif isinstance(data, list):
                        all_tasks = data
                    else:
                        all_tasks = []
                    completed_tasks_from_file = [task for task in all_tasks if task.get("status") == "已完成"]

                    # 在更新 self.tasks 之前先清空它
                    self.tasks = []
                    # 將載入的已完成任務添加到 self.tasks 列表
                    self.tasks.extend(completed_tasks_from_file)
                    self.display_tasks(completed_tasks_from_file)
                except json.JSONDecodeError:
                    messagebox.showerror("錯誤", "tasks.json 檔案格式錯誤。")
        else:
            messagebox.showerror("錯誤", "tasks.json 檔案不存在。")
        self.current_filter = {"priority": None, "group": None, "status": "已完成"} # 更新篩選狀態
        print("load_completed_tasks 函數結束") # 添加調試資訊
        
    def update_tasks_group(self, old_group_name, new_group_name=None, removing=False):
        """
        更新指定群組的所有任務的群組名稱，或在移除群組時將相關任務的群組設定為 "無"。

        Args:
            old_group_name (str): 要更新或移除的舊群組名稱。
            new_group_name (str, optional): 新的群組名稱。如果為 None 且 removing 為 False，則不更改名稱。默認為 None。
            removing (bool): 指示是否正在移除群組。如果為 True，則 new_group_name 會被忽略，相關任務的群組會被設定為 "無"。默認為 False。
        """
        updated_tasks = []
        for task in self.all_tasks:
            original_group = task.get('group')
            if task.get('group') == old_group_name:
                if removing:
                    task['group'] = "無"
                elif new_group_name is not None:
                    task['group'] = new_group_name
                if task.get('group') != original_group: # 如果群組有變更，則更新 JSON
                    self.update_task_in_json(task)
            updated_tasks.append(task)
        self.all_tasks = updated_tasks # 更新 all_tasks 列表
        self.apply_filter() # 重新應用篩選以更新 Treeview 顯示

    def update_filtered_task_list(self, filtered_tasks):
            """更新篩選後的任務列表顯示 (修正遺失 id 的問題)"""
            for item in self.treeview.get_children():
                self.treeview.delete(item)

            for task in filtered_tasks:
                task_id = task.get('id')  # 獲取任務的 id
                values = (
                    task.get('name', ''),
                    task.get('priority', ''),
                    task.get('deadline', ''),
                    task.get('status', ''),
                    task.get('group', '無') if "group" in task else '無'
                )
                tags = ()
                if task.get('status') == "未動工":
                    tags = ("undone",)
                elif task.get('status') == "已完成":
                    tags = ("completed",)
                elif task.get('status') == "任務暫停":
                    tags = ("pause",)

                self.treeview.insert("", "end", text=task_id, values=values, tags=tags) # 設置 text 屬性為 task_id

            self.treeview.column("name", anchor="w")
            self.treeview.column("priority", anchor="center")
            self.treeview.column("deadline", anchor="center")
            self.treeview.column("status", anchor="center")
            self.treeview.column("group", anchor="w")
    
    def display_tasks(self, tasks_to_display):
        """顯示指定的任務列表"""
        # 清空 Treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        for task in tasks_to_display:
            tags = ()
            if task.get("status") == "未動工":
                tags = ("undone",)  # 應用 "undone" 標籤
            elif task.get("status") == "已完成":
                tags = ("completed",)
            elif task.get("status") == "任務暫停":
                tags = ("pause",)

            self.treeview.insert(
                "",
                tk.END,
                text=task.get("id"),
                values=(
                    task.get("name", ""),
                    task.get("priority", ""),
                    task.get("deadline", ""),
                    task.get("status", ""),
                    task.get("group", ""),
                ),
                tags=tags,  # 將標籤傳遞給 insert 方法
            )
    
    def remove_task_from_json(self, task_index):
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", "tasks.json")

        # 讀取 .json 檔案
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}  # 如果 JSON 格式錯誤，初始化為空字典
        else:
            data = {}  # 如果檔案不存在，初始化為空字典

        # 獲取 "tasks" 列表，如果不存在則創建一個空列表
        tasks = data.get("tasks", [])

        # 確保 task_index 在有效範圍內
        if 0 <= task_index < len(tasks):
            # 從任務列表中移除任務 (移除包含 "task" 的整個字典)
            del tasks[task_index]

            # 更新 "tasks" 列表
            data["tasks"] = tasks

            # 將更新後的 JSON 資料寫回檔案
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
    #-------------------------------------------------------------------------------------------------------------       
    # 頂欄篩選功能函數 & 單選排序功能
    def filter_priority(self):
        """篩選優先級"""
        priorities = ["展示所有未完成任務", "本日必做", "最高", "高", "中", "低"]  # 新增展示所有未完成任務
        filter_window = FilterWindow(self.root, priorities, self._filter_tasks_by_priority)

    def filter_group(self):
        """篩選群組"""
        groups = ["展示所有未完成任務"]
        app_groups = sorted(self.groups)  # 從 self.app 獲取最新的群組列表並排序
        if "無" in app_groups:
            groups.append("無")
            remaining_groups = [group for group in app_groups if group != "無"]
            groups.extend(remaining_groups)
        else:
            groups.extend(app_groups)

        # 確保 "展示所有未完成任務" 出現在最前面
        if "展示所有未完成任務" in groups and groups.index("展示所有未完成任務") != 0:
            groups.remove("展示所有未完成任務")
            groups.insert(0, "展示所有未完成任務")

        filter_window = FilterWindow(self.root, groups, self._filter_tasks_by_group)

    def filter_status(self):
        """篩選狀態"""
        statuses = ["展示所有未完成任務", "未動工", "釐清中", "動工中", "待回報", "檢驗中", "已完成", "外包中", "擱置中", "任務暫停"] # 新增展示所有未完成任務
        filter_window = FilterWindow(self.root, statuses, self._filter_tasks_by_status)

    def _filter_tasks_by_priority(self, selected_priority):
        """按優先級篩選任務"""
        if selected_priority == "展示所有未完成任務":
            self.current_filter["priority"] = None
        else:
            self.current_filter["priority"] = selected_priority
        self.apply_filter()

    def _filter_tasks_by_group(self, selected_group):
        """按群組篩選任務"""
        if selected_group == "展示所有未完成任務":
            self.current_filter["group"] = None
        else:
            self.current_filter["group"] = selected_group
        self.apply_filter()

    def _filter_tasks_by_status(self, selected_status):
        """篩選狀態"""
        if selected_status == "展示所有未完成任務":
            self.current_filter["status"] = None
        elif selected_status == "已完成":
            self.current_filter["status"] = "已完成"
        else:
            self.current_filter["status"] = selected_status
        self.apply_filter()

    def apply_filter(self):
        """應用當前的篩選條件並更新 Treeview 和標題樣式"""
        filtered_tasks = self.all_tasks
        if self.current_filter["priority"]:
            filtered_tasks = [task for task in filtered_tasks if task['priority'] == self.current_filter["priority"]]
        if self.current_filter["group"]:
            filtered_tasks = [task for task in filtered_tasks if task.get('group', '無') == self.current_filter["group"]]
        if self.current_filter["status"]:
            if self.current_filter["status"] == "展示所有未完成任務":
                filtered_tasks = [task for task in filtered_tasks if task.get('status') != "已完成"]
            else:
                filtered_tasks = [task for task in filtered_tasks if task['status'] == self.current_filter["status"]]
        else:
            filtered_tasks = [task for task in filtered_tasks if task.get('status') != "已完成"]

        self.tasks = filtered_tasks
        self.update_task_list()
        self._update_header_title()
    
    def sort_tasks(self):
            """根據選擇的排序方式排序任務"""
            sort_option = self.sort_option.get()

            if sort_option == "添加時間":
                if self.original_order:
                    original_order_ids = [task.get('id') for task in self.original_order if task.get('id')]
                    if original_order_ids:
                        def original_order_key(task):
                            task_id = task.get('id')
                            try:
                                index = original_order_ids.index(task_id)
                                return index
                            except ValueError:
                                print(f"  警告：task id '{task_id}' 不在 original_order_ids 中")
                                return float('inf') # 如果 task 的 id 不在 original_order 中，排在最後
                        self.tasks.sort(key=original_order_key)
                    else:
                        print("警告：original_order_ids 為空")
            elif sort_option == "優先級":
                # 按優先級排序
                priority_order = {"本日必做": 0, "最高": 1, "高": 2, "中": 3, "低": 4}
                self.tasks.sort(key=lambda task: priority_order.get(task['priority'], 5))
            elif sort_option == "截止時間":
                # 按截止時間排序
                
                def deadline_key(task):
                    deadline_str = task.get('deadline', '無')
                    if deadline_str == "無":
                        return datetime.max
                    else:
                        try:
                            return datetime.strptime(deadline_str, "%Y-%m-%d-%H:%M")
                        except ValueError:
                            return datetime.max
                self.tasks.sort(key=deadline_key)

            self.update_task_list()
    
    #-------------------------------------------------------------------------------------------------------------             

        

    def sort_deadline(self):
        """排序截止日，'無' 截止日期的任務排在最後"""
        def deadline_key(task):
            if task['deadline'] == "無":
                return datetime.max  # 將 '無' 視為最大日期，排在最後
            else:
                try:
                    return datetime.strptime(task['deadline'], "%Y-%m-%d-%H:%M")
                except ValueError:
                    return datetime.max # 如果格式不正確，也排在最後

        self.tasks.sort(key=deadline_key, reverse=not self.sort_order)
        self.sort_order = not self.sort_order
        self.update_task_list()

        
    def _update_header_title(self):
        """根據篩選狀態更新 Treeview 的標題文字"""
        priority_text = "優先級"
        group_text = "群組"
        status_text = "狀態"

        if self.current_filter["priority"] and self.current_filter["priority"] != "展示所有未完成任務":
            priority_text = "優先級(篩)"
        if self.current_filter["group"] and self.current_filter["group"] != "展示所有未完成任務":
            group_text = "群組(篩)"
        if self.current_filter["status"] and self.current_filter["status"] != "展示所有未完成任務":
            status_text = "狀態(篩)"

        self.treeview.heading("priority", text=priority_text, command=lambda: self.filter_priority())
        self.treeview.heading("deadline", text="截止日", command=lambda: self.sort_deadline())
        self.treeview.heading("status", text=status_text, command=self.filter_status)
        self.treeview.heading("group", text=group_text, command=lambda: self.filter_group())
        


    def manage_group(self, task_index):
        """將任務管理群組"""
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", "tasks.json")
        group_window = GroupWindow(self.app.root, self)
        self.app.root.wait_window(group_window.top)

    def open_add_task_window(self):
        self.add_task_window = AddTaskWindow(self.root, self.add_task, self.app, self.groups)

    def on_add_task_window_close(self):
        self.add_task_window_open = False
        self.add_task_window.top.destroy()

    def add_task(self, task_data):
        """新增任務"""
        task_data["status"] = "未動工"
        self.tasks.insert(0, task_data)
        self.original_order.insert(0, task_data)
        self.all_tasks.insert(0, task_data)  # 將新任務也添加到 self.all_tasks
        self.update_task_list()  # 直接更新 Treeview

    def move_task_to_front(self, task):
        """將任務移到列表開頭，使用任務 ID 匹配"""
        task_id = task["id"]

        # 使用任務 ID 在 self.tasks 中尋找並移除
        for i, t in enumerate(self.tasks):
            if "id" in t: #確認"id"鍵是否存在
                if t["id"] == task_id:
                    removed_task = self.tasks.pop(i)
                    self.tasks.insert(0, removed_task)
                    break

        # 使用任務 ID 在 self.original_order 中尋找並移除
        for i, t in enumerate(self.original_order):
            if "id" in t: #確認"id"鍵是否存在
                if t["id"] == task_id:
                    removed_task = self.original_order.pop(i)
                    self.original_order.insert(0, removed_task)
                    break

        self.update_task_list()
        self.treeview.update_idletasks() #強制更新treeview
        self.treeview.update() #強制更新treeview
        self.treeview.delete(*self.treeview.get_children()) #強制清除treeview所有項目
        self.update_task_list() #重新插入資料

    def change_task_info(self, task, task_index):
        """變更任務優先級和狀態"""
        status_window = ChangeStatusWindow(self, task, task_index, self.app, self.groups)

    def show_right_click_menu(self, event):
            try:
                selected_item = self.treeview.identify_row(event.y)
                if selected_item:
                    task_id = self.treeview.item(selected_item, 'text')

                    if task_id:
                        task_to_edit = None
                        task_index = -1
                        for i, task in enumerate(self.tasks):
                            if task.get('id') == task_id:
                                task_to_edit = task
                                task_index = i
                                break

                        if task_to_edit:
                            menu = tk.Menu(self.root, tearoff=0)
                            menu.add_command(label="變更任務資訊", command=lambda: self.open_edit_window(task_to_edit, task_index))                            
                            menu.add_command(label="任務備註", command=lambda: self.view_or_edit_note(task_to_edit))
                            menu.add_command(label="任務記錄", command=lambda: self.view_progress_tracking(task_to_edit))
                            menu.add_command(label="管理群組", command=lambda: self.manage_group(task_index))
                            menu.add_command(label="移除任務", command=lambda: self.remove_task_by_id(task_to_edit.get('id')))
                            menu.post(event.x_root, event.y_root)
                        else:
                            messagebox.showerror("錯誤", f"找不到 ID 為 '{task_id}' 的任務。")
                    else:
                        print("警告：選中項目沒有 ID。")
                else:
                    print("警告：沒有選中任何項目。")
            except IndexError:
                pass

    def open_edit_window(self, task_to_edit, task_index):
        ChangeStatusWindow(self, task_to_edit, task_index, self.app, self.groups)

    def remove_task_by_id(self, task_id_to_remove):
            """根據任務 ID 移除任務"""
            if messagebox.askyesno("確認", "確定要移除任務嗎？（此操作無法復原）"):
                original_len_tasks = len(self.tasks)
                self.tasks = [task for task in self.tasks if task.get('id') != task_id_to_remove]
                if len(self.tasks) < original_len_tasks:
                    original_len_all_tasks = len(self.all_tasks)
                    self.all_tasks = [task for task in self.all_tasks if task.get('id') != task_id_to_remove]
                    if len(self.all_tasks) < original_len_all_tasks:
                        self.remove_task_from_json_by_id(task_id_to_remove)
                        self.update_task_list()
                    else:
                        print(f"警告：ID 為 '{task_id_to_remove}' 的任務在 self.tasks 中被移除，但在 self.all_tasks 中未找到。")
                else:
                    messagebox.showerror("錯誤", f"找不到 ID 為 '{task_id_to_remove}' 的任務以進行移除。")

    def remove_task_from_json_by_id(self, task_id):
        """根據任務 ID 從 .json 檔案中移除任務"""
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", "tasks.json")
        if os.path.exists(filename):
            with open(filename, "r+", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    tasks = data.get("tasks", [])
                    updated_tasks = [item for item in tasks if item.get("task", {}).get("id") != task_id]
                    data["tasks"] = updated_tasks
                    f.seek(0)
                    json.dump(data, f, ensure_ascii=False, indent=4)
                    f.truncate()
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"移除 tasks.json 任務時發生錯誤：{e}")

    def load_tasks_from_json(self):
            """從 tasks.json 檔案載入任務和群組，並在載入後應用篩選"""
            filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", "tasks.json")

            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        loaded_tasks = []
                        if isinstance(data, dict):
                            loaded_tasks = [item["task"] for item in data.get("tasks", [])]
                            self.groups = data.get("groups", ["無"])
                        elif isinstance(data, list):
                            loaded_tasks = data
                            self.groups = ["無"]
                        else:
                            self.tasks = []
                            self.groups = ["無"]

                        self.all_tasks = loaded_tasks # 填充所有任務列表
                        self.tasks = loaded_tasks.copy() # 初始化時，顯示所有任務
                        self.original_order = self.tasks.copy()
                        self.sort_tasks()  # 載入後立即排序
                        self.apply_filter() # 載入後應用當前篩選
                        return
                    except json.JSONDecodeError:
                        self.tasks = []
                        self.all_tasks = []
                        self.groups = ["無"]
            else:
                self.tasks = []
                self.all_tasks = []
                self.groups = ["無"]

            self.original_order = self.tasks.copy()
            self.sort_tasks()
            self.apply_filter()

    def update_task_list(self):
        """更新任務列表顯示並嘗試保持選定狀態 (id 儲存在 item 的 text 屬性中) - 修正 id 讀取"""

        # 獲取目前選定的項目的 ID
        selected_items = self.treeview.selection()
        previously_selected_id = None
        if selected_items:
            previously_selected_item = selected_items[0]
            previously_selected_id = self.treeview.item(previously_selected_item, 'text')

        # 清除現有的資料
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # 儲存 task id 和 Treeview item id 的對應關係
        item_id_map = {}

        for task in self.tasks:  # 直接迭代 self.tasks 中的任務字典
            task_id = task.get('id')
            values = (
                task.get('name', ''),
                task.get('priority', ''),
                task.get('deadline', ''),
                task.get('status', ''),
                task.get('group', '')
            )
            tags = ()
            if task.get('status') == "未動工":
                tags = ("undone",)
            elif task.get('status') == "已完成":
                tags = ("completed",)
            elif task.get('status') == "任務暫停":
                tags = ("pause",)

            try:
                item_id = self.treeview.insert("", "end", text=task_id, values=values, tags=tags)
                item_id_map[task_id] = item_id
            except Exception as e:
                import traceback
                traceback.print_exc()
                break # 如果插入失敗，停止後續插入

        # 設定欄位文字置中
        self.treeview.column("name", anchor="w")
        self.treeview.column("priority", anchor="center")
        self.treeview.column("deadline", anchor="center")
        self.treeview.column("status", anchor="center")
        self.treeview.column("group", anchor="w")

        # 嘗試重新選中之前的項目
        if previously_selected_id and previously_selected_id in item_id_map:
            new_selected_item = item_id_map[previously_selected_id]
            self.treeview.selection_set(new_selected_item)
            self.treeview.see(new_selected_item) # 確保它在可見範圍內

        self.treeview.event_generate('<<TreeviewSelect>>') # 嘗試觸發 Treeview 更新事件
        self.treeview.after(0, self.treeview.update) # 延遲到下一個事件循環執行

    def view_or_edit_note(self, task):
        """查看或修改任務備註"""
        note_window = ModifyNoteWindow(self.root, task)

    def view_progress_tracking(self, task):
        """查看任務記錄"""
        progress_window = ProgressTrackingWindow(self.root, task, self.update_task_in_json)
        
#-----------------------------------------------------------
    def _open_merge_export_window(self):
        """
        開啟任務匯出/匯入/合併視窗。
        """
        TaskMergeExportWindow(self)
        
        
    # def export_filtered_tasks(self):
    #     """
    #     將目前篩選後的任務匯出到一個 JSON 檔案，
    #     只包含篩選任務中實際使用的群組。
    #     """
    #     if not self.tasks:
    #         messagebox.showinfo("匯出任務", "目前沒有篩選後的任務可以匯出。")
    #         return

    #     file_path = filedialog.asksaveasfilename(
    #         defaultextension=".json",
    #         filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
    #         title="儲存篩選後的任務",
    #         initialfile="filtered_tasks.json"
    #     )

    #     if file_path:
    #         # 1. 提取篩選後任務中實際使用的群組
    #         used_groups = set()
    #         for task_data in self.tasks:
    #             group = task_data.get('group')
    #             if group: # 檢查群組是否存在且非空
    #                 used_groups.add(group)
            
    #         # 將集合轉換為列表並排序，確保 "無" 在最前面（如果存在）
    #         export_groups = sorted(list(used_groups))
    #         if "無" in export_groups:
    #             export_groups.remove("無")
    #             export_groups.insert(0, "無")


    #         # 2. 準備匯出的資料結構
    #         # 為了與您的 tasks.json 格式保持一致，我們將每個任務包裝在 "task" 鍵下
    #         export_data = {
    #             "tasks": [{"task": t} for t in self.tasks],
    #             "groups": export_groups # 只匯出這些任務中使用的群組
    #         }

    #         try:
    #             with open(file_path, "w", encoding="utf-8") as f:
    #                 json.dump(export_data, f, indent=4, ensure_ascii=False)
    #             messagebox.showinfo("匯出成功", f"篩選後的任務已成功匯出到：\n{file_path}")
    #         except Exception as e:
    #             messagebox.showerror("匯出錯誤", f"匯出任務時發生錯誤：\n{e}")
                
class TaskMergeExportWindow:
    def __init__(self, parent_task_instance):
        # parent_task_instance 是 Task 類別的實例，用於存取任務數據和方法
        self.task_manager = parent_task_instance
        self.top = tk.Toplevel(parent_task_instance.root) # 使用 Task 實例的 root 作為父視窗
        self.top.title("任務協作工具")
        self.top.transient(parent_task_instance.root) # 讓視窗保持在父視窗上方
        self.top.grab_set() # 模式視窗，阻止與主視窗的互動

        self.notebook = ttk.Notebook(self.top)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # 匯出頁籤
        self.export_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.export_frame, text="匯出任務")
        self._create_export_tab(self.export_frame)

        # 匯入頁籤
        self.import_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.import_frame, text="匯入任務")
        self._create_import_tab(self.import_frame)

        # 合併頁籤
        self.merge_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.merge_frame, text="合併任務")
        self._create_merge_tab(self.merge_frame)

        # 合併功能相關的暫存列表
        self.files_to_merge = []

        # 確保關閉視窗時釋放 grab
        self.top.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        """處理視窗關閉事件，釋放 grab"""
        self.top.grab_release()
        self.top.destroy()

    # --- 匯出功能 ---
    def _create_export_tab(self, parent_frame):
        tk.Label(parent_frame, text="請選擇匯出方式：", font=("Arial", 10, "bold")).pack(pady=10)

        self.export_option = tk.StringVar(value="keep") # 預設為不移除

        tk.Radiobutton(parent_frame, text="匯出後不移除任務", variable=self.export_option, value="keep").pack(anchor="w", padx=20)
        tk.Radiobutton(parent_frame, text="匯出後移除任務 (不可復原)", variable=self.export_option, value="remove").pack(anchor="w", padx=20)

        ttk.Button(parent_frame, text="開始匯出", command=self._perform_export).pack(pady=15)

    def _perform_export(self):
        if not self.task_manager.tasks: # self.tasks 是篩選後的任務列表
            messagebox.showinfo("匯出任務", "目前沒有篩選後的任務可以匯出。")
            return

        # 讓使用者選擇儲存路徑和檔案名稱
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", # <--- 已更新為 .json
            filetypes=[("JSON files", "*.json"), ("所有檔案", "*.*")], # <--- 已更新為 .json
            title="儲存篩選後的任務",
            initialfile="exported_tasks.json" # <--- 已更新為 .json
        )

        if not file_path:
            return # 使用者取消儲存

        # 提取篩選後任務中實際使用的群組
        used_groups = set()
        for task_data in self.task_manager.tasks:
            group = task_data.get('group')
            if group:
                used_groups.add(group)

        export_groups = sorted(list(used_groups))
        if "無" in export_groups:
            export_groups.remove("無")
            export_groups.insert(0, "無")

        export_data = {
            "tasks": [{"task": t} for t in self.task_manager.tasks],
            "groups": export_groups
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)

            if self.export_option.get() == "remove":
                if messagebox.askyesno("確認移除", "匯出完成！您選擇了匯出後移除任務。\n\n確定要從原任務列表中移除這些任務嗎？此操作不可復原！"):
                    # 遍歷 self.task_manager.tasks (篩選後的任務) 進行移除
                    # 避免在迭代時修改列表，先收集要移除的 ID
                    ids_to_remove = [task.get('id') for task in self.task_manager.tasks]
                    for task_id in ids_to_remove:
                        self.task_manager.remove_task_from_json_by_id(task_id)
                        # 從 Task 實例的內部列表也移除
                        self.task_manager.all_tasks = [t for t in self.task_manager.all_tasks if t.get('id') != task_id]
                        self.task_manager.original_order = [t for t in self.task_manager.original_order if t.get('id') != task_id]
                    
                    self.task_manager.apply_filter() # 重新應用篩選以更新 Treeview
                    messagebox.showinfo("匯出與移除", "任務已成功匯出並從原列表中移除。")
                else:
                    messagebox.showinfo("匯出完成", "任務已成功匯出，但未從原列表中移除。")
            else:
                messagebox.showinfo("匯出成功", f"篩選後的任務已成功匯出到：\n{file_path}\n\n任務已保留在原列表中。")

        except Exception as e:
            messagebox.showerror("匯出錯誤", f"匯出任務時發生錯誤：\n{e}")

    # --- 匯入功能 ---
    def _create_import_tab(self, parent_frame):
        tk.Label(parent_frame, text="請選擇匯入方式：", font=("Arial", 10, "bold")).pack(pady=10)

        self.import_option = tk.StringVar(value="keep") # 預設為不移除

        tk.Radiobutton(parent_frame, text="匯入後不移除原檔案", variable=self.import_option, value="keep").pack(anchor="w", padx=20)
        tk.Radiobutton(parent_frame, text="匯入後移除原檔案 (不可復原)", variable=self.import_option, value="remove").pack(anchor="w", padx=20)

        ttk.Button(parent_frame, text="選擇檔案並匯入", command=self._perform_import).pack(pady=15)

    def _perform_import(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("所有檔案", "*.*")], # <--- 已更新為 .json
            title="選擇要匯入的任務檔案"
        )

        if not file_path:
            return # 使用者取消選擇

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            imported_tasks_data = import_data.get("tasks", [])
            imported_groups_data = import_data.get("groups", [])

            new_tasks_count = 0
            # 遍歷匯入的任務，並添加到 self.task_manager 的 all_tasks 和 original_order 中
            # 同時避免重複任務 (根據 id 判斷)
            existing_task_ids = {t.get('id') for t in self.task_manager.all_tasks}

            tasks_to_add = []
            for item in imported_tasks_data:
                task = item.get("task")
                if task and task.get('id') not in existing_task_ids:
                    tasks_to_add.append(task)
                    existing_task_ids.add(task.get('id')) # 更新已存在的 ID 集合
                    new_tasks_count += 1
            
            # 將新任務添加到 all_tasks 和 original_order
            self.task_manager.all_tasks.extend(tasks_to_add)
            self.task_manager.original_order.extend(tasks_to_add) # 保持原始順序
            # 由於 self.tasks 是篩選後的，重新載入或應用篩選會更新它
            
            # 合併群組列表，並更新 task_manager 中的 groups
            # 使用 set 來處理重複，然後轉換回列表並排序
            updated_groups_set = set(self.task_manager.groups)
            updated_groups_set.update(imported_groups_data)
            self.task_manager.groups = sorted(list(updated_groups_set))
            if "無" in self.task_manager.groups:
                self.task_manager.groups.remove("無")
                self.task_manager.groups.insert(0, "無")


            # 將更新後的 all_tasks 寫回 tasks.json
            self._save_all_tasks_to_json() # 這是 Task 類別中應該有的私有方法來儲存 all_tasks

            # 更新 Treeview 顯示
            self.task_manager.apply_filter()

            # 處理匯入後是否移除原檔案
            if self.import_option.get() == "remove":
                if messagebox.askyesno("確認移除原檔案", f"任務已成功匯入 ({new_tasks_count} 個新任務)。\n\n您選擇了匯入後移除原檔案。\n確定要刪除原始檔案：\n{file_path}\n\n此操作不可復原！"):
                    os.remove(file_path)
                    messagebox.showinfo("匯入與移除", f"任務已成功匯入，原始檔案 '{os.path.basename(file_path)}' 已被移除。")
                else:
                    messagebox.showinfo("匯入完成", f"任務已成功匯入 ({new_tasks_count} 個新任務)，但原始檔案未被移除。")
            else:
                messagebox.showinfo("匯入成功", f"任務已成功匯入 ({new_tasks_count} 個新任務)。")

        except json.JSONDecodeError:
            messagebox.showerror("匯入錯誤", f"選取的檔案 '{os.path.basename(file_path)}' 不是有效的 JSON 格式。")
        except FileNotFoundError:
            messagebox.showerror("匯入錯誤", "檔案不存在。")
        except Exception as e:
            messagebox.showerror("匯入錯誤", f"匯入任務時發生錯誤：\n{e}")

    # --- 合併功能 ---
    def _create_merge_tab(self, parent_frame):
            tk.Label(parent_frame, text="選擇要合併的任務檔案：", font=("Arial", 10, "bold")).pack(pady=10)

            add_file_button = ttk.Button(parent_frame, text="選取任務檔", command=self._select_merge_files)
            add_file_button.pack(pady=5)

            self.merge_listbox_frame = tk.Frame(parent_frame)
            self.merge_listbox_frame.pack(expand=True, fill="both", padx=20, pady=5)

            self.merge_listbox_scrollbar = tk.Scrollbar(self.merge_listbox_frame)
            self.merge_listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.merge_listbox = tk.Listbox(
                self.merge_listbox_frame,
                yscrollcommand=self.merge_listbox_scrollbar.set,
                height=8, # 可見行數
                relief="groove",
                borderwidth=1
            )
            self.merge_listbox.pack(expand=True, fill="both")
            self.merge_listbox_scrollbar.config(command=self.merge_listbox.yview)

            # 右鍵選單用於移除選定的檔案
            self.merge_listbox.bind("<Button-3>", self._show_merge_listbox_context_menu)

            start_merge_button = ttk.Button(parent_frame, text="開始合併", command=self._start_merge)
            start_merge_button.pack(pady=15)

    def _select_merge_files(self):
            # *** 修改後的防禦性檢查 ***
            if self.merge_listbox is None:
                messagebox.showerror("UI 錯誤", "合併任務列表未正確初始化。請重新啟動視窗或檢查程式碼。")
                print("ERROR: self.merge_listbox is None in _select_merge_files. This should not happen if _create_merge_tab ran correctly.")
                return # 停止執行，因為 Listbox 不存在

            selected_files = filedialog.askopenfilenames(
                filetypes=[("JSON files", "*.json"), ("所有檔案", "*.*")],
                title="選擇要合併的任務檔案"
            )
            if selected_files:
                for f_path in selected_files:
                    if f_path not in self.files_to_merge: # 避免重複添加
                        self.files_to_merge.append(f_path)
                        self.merge_listbox.insert(tk.END, os.path.basename(f_path)) # 顯示檔案名稱

    def _show_merge_listbox_context_menu(self, event):
        # 顯示右鍵選單以移除列表中的檔案
        try:
            index = self.merge_listbox.nearest(event.y)
            if index != -1: # 確保有項目被點擊
                self.merge_listbox.selection_clear(0, tk.END) # 清除所有選擇
                self.merge_listbox.selection_set(index) # 選中點擊的項目
                
                menu = tk.Menu(self.top, tearoff=0)
                menu.add_command(label="從列表中移除", command=lambda: self._remove_selected_merge_file(index))
                menu.post(event.x_root, event.y_root)
        except IndexError:
            pass # 沒有點擊到有效的項目


    def _remove_selected_merge_file(self, index):
        if 0 <= index < len(self.files_to_merge):
            del self.files_to_merge[index]
            self.merge_listbox.delete(index)


    def _start_merge(self):
        if not self.files_to_merge:
            messagebox.showinfo("合併任務", "請先選擇要合併的任務檔案。")
            return

        # 提示使用者選擇儲存合併後檔案的路徑和名稱
        output_file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("所有檔案", "*.*")],
            title="儲存合併後的任務檔案",
            initialfile="merged_tasks.json"
        )

        if not output_file_path:
            return # 使用者取消儲存

        confirm = messagebox.askokcancel(
            "確認合併並儲存",
            f"確定要將選定的 {len(self.files_to_merge)} 個任務檔案合併到新檔案嗎？\n\n合併後的檔案將儲存到：\n{output_file_path}"
        )
        if not confirm:
            return

        merged_tasks = []
        merged_groups_set = set()
        seen_task_ids = set() # 用於追蹤已添加的任務 ID，避免重複

        processed_files_count = 0
        skipped_files_count = 0

        for file_path in self.files_to_merge:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    merge_data = json.load(f)

                current_file_tasks_data = merge_data.get("tasks", [])
                current_file_groups_data = merge_data.get("groups", [])

                for item in current_file_tasks_data:
                    task = item.get("task")
                    if task and task.get('id') not in seen_task_ids:
                        merged_tasks.append(task)
                        seen_task_ids.add(task.get('id'))
                
                merged_groups_set.update(current_file_groups_data)
                processed_files_count += 1

            except json.JSONDecodeError:
                messagebox.showwarning("合併警告", f"檔案 '{os.path.basename(file_path)}' 不是有效的 JSON 格式，已跳過。")
                skipped_files_count += 1
            except FileNotFoundError:
                messagebox.showwarning("合併警告", f"檔案 '{os.path.basename(file_path)}' 不存在，已跳過。")
                skipped_files_count += 1
            except Exception as e:
                messagebox.showwarning("合併警告", f"處理檔案 '{os.path.basename(file_path)}' 時發生錯誤：\n{e}\n已跳過。")
                skipped_files_count += 1
        
        # 將群組轉換為列表並排序，確保「無」在最前面
        final_merged_groups = sorted(list(merged_groups_set))
        if "無" in final_merged_groups:
            final_merged_groups.remove("無")
            final_merged_groups.insert(0, "無")

        merged_output_data = {
            "tasks": [{"task": t} for t in merged_tasks],
            "groups": final_merged_groups
        }

        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(merged_output_data, f, indent=4, ensure_ascii=False)

            messagebox.showinfo(
                "合併完成",
                f"已成功將 {processed_files_count} 個檔案合併，並儲存到：\n{output_file_path}\n\n"
                f"共新增 {len(merged_tasks)} 個不重複的任務。\n"
                f"跳過 {skipped_files_count} 個有問題的檔案。"
            )

            # 合併完成後，可以選擇清空列表框和文件列表
            self.files_to_merge = []
            self.merge_listbox.delete(0, tk.END)
            
            # 不再關閉視窗，讓使用者可以繼續操作
            # self._on_closing() 

        except Exception as e:
            messagebox.showerror("儲存錯誤", f"儲存合併後的任務檔案時發生錯誤：\n{e}")

    # --- 輔助函數 (應在 Task 類別中實現或調用 Task 的方法) ---
    def _save_all_tasks_to_json(self):
        """
        將 self.task_manager.all_tasks 和 self.task_manager.groups 儲存回 tasks.json。
        這個函數應該是 Task 類別的一個方法，或者這個類別直接調用 Task 的方法來實現。
        為了避免循環依賴或過度耦合，我將其放在這裡，但建議 Task 類別提供一個公共方法。
        """
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", "tasks.json")
        data_to_save = {
            "tasks": [{"task": t} for t in self.task_manager.all_tasks], # 儲存 all_tasks
            "groups": self.task_manager.groups
        }
        try:
            # 確保 temp 目錄存在
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("儲存錯誤", f"儲存任務數據到 tasks.json 時發生錯誤：\n{e}")



class FilterWindow: #已整理完成
    '''任務管理器的篩選功能'''
    #-------------------------------------------------------------------------------------------------------------   
    def __init__(self, parent, options, filter_callback):
        self.top = tk.Toplevel(parent)
        self.top.title("篩選")

        # 阻止視窗被縮放
        self.top.resizable(False, False)

        # 設置為 parent 的暫態子視窗
        self.top.transient(parent)

        # 強制使用者與此視窗互動
        self.top.grab_set()

        self.filter_callback = filter_callback

        self.option_combobox = ttk.Combobox(self.top, values=options, state="readonly")
        self.option_combobox.pack(padx=10, pady=10)
        self.option_combobox.set(options[0])  # 設定預設值

        self.filter_button = tk.Button(self.top, text="篩選", command=self.filter)
        self.filter_button.pack(pady=10)

        # 確保彈出框在父視窗之前
        self.top.lift(parent)

        # 程式執行停留在這個彈出框，直到它被關閉
        self.top.wait_window(self.top)
    #-------------------------------------------------------------------------------------------------------------
    def filter(self):
        """執行篩選"""
        selected_option = self.option_combobox.get()
        self.filter_callback(selected_option)
        self.top.destroy()

class GroupWindow: #已整理完成
    '''任務管理器的管理群組功能'''
    #-------------------------------------------------------------------------------------------------------------
    def __init__(self, parent, right_panel):
        self.top = tk.Toplevel(parent)
        self.top.title("管理群組")
        self.right_panel = right_panel

        # 阻止視窗被縮放
        self.top.resizable(False, False)

        # 設置為 parent 的暫態子視窗
        self.top.transient(parent)

        # 強制使用者與此視窗互動
        self.top.grab_set()

        # 提示字
        self.prompt_label = tk.Label(self.top, text="輸入群組名後添加：")
        self.prompt_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5)

        # 文字輸入框
        self.group_name_entry = tk.Entry(self.top)
        self.group_name_entry.grid(row=1, column=0, columnspan=2, pady=10, sticky=tk.EW, padx=20)

        # 增加群組和移除群組按鈕
        self.button_frame = tk.Frame(self.top)
        self.button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.add_group_button = tk.Button(self.button_frame, text="增加群組", command=self.add_group)
        self.add_group_button.grid(row=0, column=0, padx=5)

        self.remove_group_button = tk.Button(self.button_frame, text="移除群組", command=self.remove_group)
        self.remove_group_button.grid(row=0, column=1, padx=5)

        # 群組 Treeview
        self.group_treeview = ttk.Treeview(self.top, columns=("群組名稱",), show="headings")
        self.group_treeview.heading("群組名稱", text="群組名稱")
        self.group_treeview.grid(row=3, column=0, padx=(10, 0), pady=10, sticky=tk.NSEW)

        # 垂直滾動條 (使用 tk.Scrollbar)
        self.scrollbar = tk.Scrollbar(self.top, orient=tk.VERTICAL, command=self.group_treeview.yview)
        self.scrollbar.grid(row=3, column=1, padx=(0, 10), pady=10, sticky=tk.NS)

        self.group_treeview.configure(yscrollcommand=self.scrollbar.set)

        self.top.grid_rowconfigure(3, weight=1)
        self.top.grid_columnconfigure(0, weight=1)

        self.update_group_treeview()
        
        # 創建右鍵選單
        self.group_menu = tk.Menu(self.group_treeview, tearoff=0)
        self.group_menu.add_command(label="重新命名群組", command=self.rename_selected_group)
        self.group_menu.add_command(label="移除群組", command=self.remove_group)

        # 綁定右鍵點擊事件
        self.group_treeview.bind("<Button-3>", self.show_group_menu)
    #-------------------------------------------------------------------------------------------------------------
    def add_group(self):
        """增加群組"""
        group_name = self.group_name_entry.get()
        if group_name and group_name not in self.right_panel.groups:
            self.right_panel.groups.append(group_name) 
            self.right_panel.groups.sort()  # 按字首排序
            self.group_name_entry.delete(0, tk.END)  # 清除文字輸入框
            self.save_groups_to_json()  # 保存群組到 tasks.json
            self.update_group_treeview()

        elif group_name == "無":
            messagebox.showinfo("提示", "不可將群組名稱命名為「無」")
        else:
            messagebox.showinfo("提示", "群組名稱已存在或未輸入群組名。")

    def remove_group(self):
        """移除群組"""
        selected_item = self.group_treeview.selection()
        if selected_item:
            group_name = self.group_treeview.item(selected_item, "values")[0]
            if group_name == "無":
                messagebox.showinfo("提示", "「無」群組不可移除。")
            else:
                if messagebox.askyesno("確認刪除", f"是否要刪除{group_name}群組？\n該操作無法復原。"):
                    if group_name in self.right_panel.groups: # 修改這裡
                        self.right_panel.update_tasks_group(group_name, removing=True)
                        self.right_panel.groups.remove(group_name) # 修改這裡
                        self.save_groups_to_json()
                        self.update_group_treeview()
                    else:
                        messagebox.showerror("錯誤", f"群組 '{group_name}' 不存在。")
        else:
            messagebox.showinfo("提示", "請選擇下方要移除的群組。")

    def rename_selected_group(self):
            """重新命名選定的群組"""
            self.top.grab_set() # 確保 GroupWindow 仍然強制互動
            if self.selected_group_item:
                old_group_name = self.group_treeview.item(self.selected_group_item, "values")[0]
                if old_group_name != "無":
                    new_group_name = simpledialog.askstring("重新命名群組", f"將 '{old_group_name}' 重新命名為：", parent=self.top) # 確保對話框的父級是 GroupWindow
                    if new_group_name and new_group_name.strip():
                        new_group_name = new_group_name.strip()
                        if new_group_name == "無":
                            messagebox.showinfo("提示", "群組名稱不可命名為「無」。")
                        elif new_group_name != old_group_name and new_group_name not in self.right_panel.groups: # 修改這裡
                            # 更新所有屬於該群組的任務
                            self.right_panel.update_tasks_group(old_group_name, new_group_name)
                            # 更新群組列表
                            try:
                                index = self.right_panel.groups.index(old_group_name) # 修改這裡
                                self.right_panel.groups[index] = new_group_name # 修改這裡
                                self.save_groups_to_json()
                                self.update_group_treeview()
                            except ValueError:
                                messagebox.showerror("錯誤", f"群組 '{old_group_name}' 在應用程式群組列表中找不到。")
                        elif new_group_name == old_group_name:
                            messagebox.showinfo("提示", "群組名稱未更改。")
                        elif new_group_name in self.right_panel.groups: # 修改這裡
                            messagebox.showwarning("警告", f"群組 '{new_group_name}' 已存在!")
                        elif new_group_name is not None and not new_group_name.strip():
                            messagebox.showwarning("警告", "群組名稱不能為空!")
                    elif new_group_name is not None and not new_group_name.strip():
                        messagebox.showwarning("警告", "群組名稱不能為空!")
                else:
                    messagebox.showerror("錯誤", "無法重新命名預設的 '無' 群組!")
            else:
                messagebox.showinfo("提示", "請先在 Treeview 中右鍵點擊要重新命名的群組。")
            self.top.grab_set() # 再次確保 GroupWindow 強制互動

    def save_groups_to_json(self):
        """將群組保存到 tasks.json"""
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", "tasks.json")
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        except json.JSONDecodeError:
            data = {}
        data["groups"] = self.right_panel.groups
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            pass

    def show_group_menu(self, event):
        """顯示右鍵選單"""
        try:
            self.group_menu.post(event.x_root, event.y_root)
            # 直接使用 Treeview.selection() 獲取當前選中的項目
            selected_item = self.group_treeview.selection()
            if selected_item:
                self.selected_group_item = selected_item[0]  # 獲取選中的第一個項目
            else:
                print("No item selected.")
        except tk.TclError:
            print("TclError in show_group_menu")
            pass  # 如果點擊在空白區域，identify_row 可能返回空字串，導致錯誤

    def update_group_treeview(self):
        """更新群組 Treeview 並按字母順序排序"""
        self.group_treeview.delete(*self.group_treeview.get_children())
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", "tasks.json")

        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    groups = sorted(data.get("groups", ["無"])) # 讀取群組並排序
                    for group in groups:
                        if group != "無":  # 排除 "無" 群組
                            self.group_treeview.insert("", tk.END, values=(group,))
                except json.JSONDecodeError:
                    pass  # JSON 檔案格式錯誤，不處理
        else:
            pass  # JSON 檔案不存在，不處理

class AddTaskWindow: #已整理完成
    '''任務管理器的新增任務功能'''
    #-------------------------------------------------------------------------------------------------------------    
    def __init__(self, parent, add_task_callback, app, groups=None):
            self.top = tk.Toplevel(parent)
            self.top.title("新增任務")
            self.top.geometry("250x270")

            # 阻止視窗被縮放
            self.top.resizable(False, False)

            # 設置為 parent 的暫態子視窗
            self.top.transient(parent)

            # 強制使用者與此視窗互動
            self.top.grab_set()

            self.add_task_callback = add_task_callback
            self.app = app

            # 任務名稱
            self.name_label = tk.Label(self.top, text=" 任務名稱:")
            self.name_label.grid(row=0, column=0, pady=5, sticky="w")
            self.name_entry = tk.Entry(self.top, width=30)
            self.name_entry.grid(row=1, column=0, columnspan=4, padx=3, pady=5)

            # 優先級
            self.priority_label = tk.Label(self.top, text=" 優先級:")
            self.priority_label.grid(row=2, column=0, pady=5, sticky="w")
            self.priority_combobox = ttk.Combobox(self.top, values=["本日必做", "最高", "高", "中", "低"], state="readonly", width=8)
            self.priority_combobox.set("中")
            self.priority_combobox.grid(row=2, column=1, columnspan=2, pady=5, sticky="w")

            # 截止日欄位
            self.deadline_label = tk.Label(self.top, text=" 截止日:")
            self.deadline_label.grid(row=3, column=0, sticky="w")

            # 截止日單選按鈕
            self.deadline_var = tk.IntVar()
            self.no_deadline_radio = tk.Radiobutton(self.top, text="不設定截止日", variable=self.deadline_var, value=0, command=self.toggle_deadline_fields)
            self.no_deadline_radio.grid(row=4, column=0, columnspan=3, sticky="w")

            self.pick_deadline_radio = tk.Radiobutton(self.top, text="挑選截止日", variable=self.deadline_var, value=1, command=self.toggle_deadline_fields)
            self.pick_deadline_radio.grid(row=5, column=0, columnspan=3, sticky="w")

            # 年
            self.year_combobox = ttk.Combobox(self.top, values=[str(i) for i in range(2025, 2050)], state="readonly", width=5)
            self.year_combobox.grid(row=6, column=0, padx=1)

            # 月
            self.month_combobox = ttk.Combobox(self.top, values=[f"{i:02}" for i in range(1, 13)], state="readonly", width=5)
            self.month_combobox.grid(row=6, column=1, padx=1)

            # 日
            self.day_combobox = ttk.Combobox(self.top, values=[f"{i:02}" for i in range(1, 32)], state="readonly", width=5)
            self.day_combobox.grid(row=6, column=2, padx=5)

            # 時（00:00 ~ 23:00）
            self.hour_combobox = ttk.Combobox(self.top, values=[f"{i:02}:00" for i in range(24)], state="readonly", width=5)
            self.hour_combobox.grid(row=6, column=3, padx=5)

            self.groups = groups if groups is not None else ["無"]

            # 群組選擇
            self.status_label = tk.Label(self.top, text="群組：")
            self.status_label.grid(row=7, column=0, pady=5, sticky="w")

            sorted_groups = sorted(self.groups)

            # 確保 "無" 出現在最前面
            if "無" in sorted_groups:
                sorted_groups.remove("無")
                sorted_groups.insert(0, "無")
            elif not sorted_groups:
                sorted_groups = ["無"]
            elif "無" not in sorted_groups:
                sorted_groups.insert(0, "無")

            self.group_combobox = ttk.Combobox(self.top, values=sorted_groups, state="readonly", width=20)
            self.group_combobox.grid(row=7, column=1, columnspan=3, pady=5, sticky="w")
            self.group_combobox.set("無")  # 設定默認值為 "無"

            # 新增任務按鈕
            self.add_button = tk.Button(self.top, text="添加任務", command=self.add_task)
            self.add_button.grid(row=8, column=0, columnspan=5, pady=15)

            self.set_default_deadline()  # 設定預設截止時間
            self.toggle_deadline_fields()  # 初始狀態設定

            # 確保彈出框在父視窗之前
            self.top.lift(parent)

            # 程式執行停留在這個彈出框，直到它被關閉
            self.top.wait_window(self.top)
    #-------------------------------------------------------------------------------------------------------------
    def toggle_deadline_fields(self):
        """切換截止日期欄位的啟用狀態"""
        if self.deadline_var.get() == 0:
            self.year_combobox.config(state="disabled")
            self.month_combobox.config(state="disabled")
            self.day_combobox.config(state="disabled")
            self.hour_combobox.config(state="disabled")
        else:
            self.year_combobox.config(state="readonly")
            self.month_combobox.config(state="readonly")
            self.day_combobox.config(state="readonly")
            self.hour_combobox.config(state="readonly")

    def set_default_deadline(self):
        """設定預設截止時間為當下時間"""
        now = datetime.now()
        self.year_combobox.set(str(now.year))
        self.month_combobox.set(f"{now.month:02}")
        self.day_combobox.set(f"{now.day:02}")
        self.hour_combobox.set(f"{now.hour:02}:00")

    def save_task_to_json(self, task_data):
        """將任務儲存到 JSON 檔案"""
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", "tasks.json")

        # 讀取現有的任務（如果存在）
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        data = {}
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        tasks = data.get("tasks", [])
        tasks.insert(0, {"task": task_data})  # 將任務插入到列表開頭
        data["tasks"] = tasks

        # 將更新後的任務列表寫回 tasks.json 檔案
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # 確保資料夾存在
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_task(self):
        """獲取用戶輸入並新增任務"""
        name = self.name_entry.get()
        priority = self.priority_combobox.get()

        if self.deadline_var.get() == 0:
            deadline = "無"
        else:
            year = self.year_combobox.get()
            month = self.month_combobox.get()
            day = self.day_combobox.get()
            hour = self.hour_combobox.get()
            deadline = f"{year}-{month}-{day}-{hour}"

        # 獲取使用者選擇的群組
        selected_group = self.group_combobox.get()

        if name:
            task_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
            task_data = {
                "id": task_id,
                "name": name,
                "priority": priority,
                "deadline": deadline,
                "status": "未動工",
                "group": selected_group,  # 使用者選擇的群組
                "content":"",
                "note":"",
                "progress_tracking":[]
            }
            self.add_task_callback(task_data)
            self.save_task_to_json(task_data)
            self.top.destroy()
        else:
            messagebox.showwarning("警告", "任務名稱必須填寫!")

class ModifyNoteWindow: #已整理完成
    '''任務管理器的任務備註功能'''
    #-------------------------------------------------------------------------------------------------------------   
    def __init__(self, parent, task):
            self.top = tk.Toplevel(parent)
            self.top.title("任務備註")
            self.top.geometry("250x340")

            # 阻止視窗被縮放
            self.top.resizable(False, False)
            self.top.transient(parent)
            self.top.grab_set()
            self.task = task

            # 內容 Frame
            self.content_frame = tk.Frame(self.top)
            self.content_frame.pack(pady=5, expand=False) # 移除 fill

            self.content_label = tk.Label(self.content_frame, text="任務內容")
            self.content_label.pack(pady=5)

            self.content_text = tk.Text(self.content_frame, height=10, width=30)
            self.content_text.insert(1.0, self.task["content"])
            self.content_text.pack(side=tk.LEFT, expand=False) # 移除 fill

            self.content_scrollbar = tk.Scrollbar(self.content_frame, command=self.content_text.yview)
            self.content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.content_text.config(yscrollcommand=self.content_scrollbar.set)

            # 備註事項 Frame
            self.note_frame = tk.Frame(self.top)
            self.note_frame.pack(pady=5, expand=False) # 移除 fill

            self.note_label = tk.Label(self.note_frame, text="備註事項")
            self.note_label.pack(pady=5)

            self.note_text = tk.Text(self.note_frame, height=5, width=30)
            self.note_text.insert(1.0, self.task["note"])
            self.note_text.pack(side=tk.LEFT, expand=False) # 移除 fill

            self.note_scrollbar = tk.Scrollbar(self.note_frame, command=self.note_text.yview)
            self.note_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.note_text.config(yscrollcommand=self.note_scrollbar.set)

            # 保存按鈕
            self.save_button = tk.Button(self.top, text="保存備註", command=self.save_note)
            self.save_button.pack(pady=10)

            self.top.lift(parent)
            self.top.wait_window(self.top)
    #-------------------------------------------------------------------------------------------------------------
    def save_note(self):
        """保存修改的備註"""
        self.task["content"] = self.content_text.get("1.0", tk.END).strip()
        self.task["note"] = self.note_text.get("1.0", tk.END).strip()

        # 更新 .json 檔案
        # 確保 updated_task 包含 id 欄位
        if "id" not in self.task:
            self.task["id"] = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.update_json_file(self.task)
        
        self.top.destroy()  # 再銷毀視窗

    def update_json_file(self, updated_task):
        """更新 .json 檔案中的任務資訊"""
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", "tasks.json")

        # 讀取 .json 檔案中的任務列表
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        data = {}
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        tasks = data.get("tasks", [])
        # 找到要更新的任務
        for i, task in enumerate(tasks):
            if task["task"]["id"] == updated_task["id"]:  # 從 "task" 鍵中讀取任務 ID
                tasks[i]["task"] = updated_task  # 更新 "task" 鍵中的任務資訊
                break
        data["tasks"] = tasks

        # 將更新後的任務列表寫回 .json 檔案
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)        

class ChangeStatusWindow: #已整理完成
    '''任務管理器的變更任務資訊功能'''
    #-------------------------------------------------------------------------------------------------------------   
    def __init__(self, parent, task, task_index, app, groups):
            self.top = tk.Toplevel(parent.root)
            self.top.title("變更任務資訊")
            self.top.geometry("250x310")
            self.top.resizable(False, False)
            self.top.transient(parent.root)
            self.top.grab_set()

            self.task = task.copy() # 使用副本，方便比較修改
            self.original_task = {} # 先初始化為空字典

            # 從 self.parent.tasks 中找到對應的原始任務
            for t in parent.tasks:
                if t.get("id") == task.get("id"):
                    self.original_task = t.copy()
                    break

            self.task_index = task_index
            self.parent = parent
            self.app = app
            self.groups = groups # 將傳入的 groups 賦值給 self.groups

            # 任務名稱
            self.name_label = tk.Label(self.top, text=" 任務名稱:")
            self.name_label.grid(row=0, column=0, pady=5, sticky="w")
            self.name_entry = tk.Entry(self.top, width=30)
            self.name_entry.insert(0, self.task["name"])
            self.name_entry.grid(row=1, column=0, columnspan=4, padx=3, pady=5)

            # 優先級
            self.priority_label = tk.Label(self.top, text=" 優先級:")
            self.priority_label.grid(row=2, column=0, pady=5, sticky="w")
            self.priority_combobox = ttk.Combobox(self.top, values=["本日必做", "最高", "高", "中", "低"], state="readonly", width=8)
            self.priority_combobox.set(self.task.get("priority", "中"))
            self.priority_combobox.grid(row=2, column=1, columnspan=2, pady=5, sticky="w")

            # 截止日欄位
            self.deadline_label = tk.Label(self.top, text=" 截止日:")
            self.deadline_label.grid(row=3, column=0, sticky="w")

            # 截止日單選按鈕
            self.deadline_var = tk.IntVar()
            self.no_deadline_radio = tk.Radiobutton(self.top, text="不設定截止日", variable=self.deadline_var, value=0, command=self.toggle_deadline_fields)
            self.no_deadline_radio.grid(row=4, column=0, columnspan=3, sticky="w")
            self.pick_deadline_radio = tk.Radiobutton(self.top, text="挑選截止日", variable=self.deadline_var, value=1, command=self.toggle_deadline_fields)
            self.pick_deadline_radio.grid(row=5, column=0, columnspan=3, sticky="w")

            # 年
            self.year_combobox = ttk.Combobox(self.top, values=[str(i) for i in range(2025, 2050)], state="readonly", width=5)
            self.year_combobox.grid(row=6, column=0, padx=1)

            # 月
            self.month_combobox = ttk.Combobox(self.top, values=[f"{i:02}" for i in range(1, 13)], state="readonly", width=5)
            self.month_combobox.grid(row=6, column=1, padx=1)

            # 日
            self.day_combobox = ttk.Combobox(self.top, values=[f"{i:02}" for i in range(1, 32)], state="readonly", width=5)
            self.day_combobox.grid(row=6, column=2, padx=5)

            # 時（00:00 ~ 23:00）
            self.hour_combobox = ttk.Combobox(self.top, values=[f"{i:02}:00" for i in range(24)], state="readonly", width=5)
            self.hour_combobox.grid(row=6, column=3, padx=5)

            # 群組選擇
            self.group_label = tk.Label(self.top, text=" 群組：")
            self.group_label.grid(row=7, column=0, pady=10, sticky="w")

            groups_for_combobox = list(self.groups) # 直接使用 self.groups

            # 對群組列表進行排序
            sorted_groups = sorted(groups_for_combobox)

            # 確保 "無" 出現在最前面
            if "無" in sorted_groups:
                sorted_groups.remove("無")
                sorted_groups.insert(0, "無")
            elif not sorted_groups:
                sorted_groups = ["無"]
            elif "無" not in sorted_groups:
                sorted_groups.insert(0, "無")

            self.group_combobox = ttk.Combobox(self.top, values=sorted_groups, state="readonly", width=20)
            self.group_combobox.set(self.task.get("group", "無"))
            self.group_combobox.grid(row=7, column=1, columnspan=3, pady=5, sticky="w")

            # 狀態選擇
            self.status_label = tk.Label(self.top, text="狀態：")
            self.status_label.grid(row=8, column=0, pady=10, sticky="w")
            self.status_combobox = ttk.Combobox(self.top, values=["未動工", "釐清中", "動工中", "待回報", "檢驗中", "已完成", "外包中", "擱置中", "任務暫停"], state="readonly", width=8)
            self.status_combobox.set(self.task["status"])
            self.status_combobox.grid(row=8, column=1, columnspan=2, pady=5, sticky="w")

            # 確認按鈕
            self.confirm_button = tk.Button(self.top, text="確認", command=self.change_status)
            self.confirm_button.grid(row=9, column=0, columnspan=5, pady=15)

            self.set_default_deadline()
            self.toggle_deadline_fields()

            self.top.resizable(False, False)
            self.top.transient(parent.root)
            self.top.grab_set()
            self.top.lift(parent.root)
            self.top.wait_window(self.top)
    #-------------------------------------------------------------------------------------------------------------
    def change_status(self):
        """更新任務資訊，並根據當前篩選狀態決定是否從 Treeview 移除"""
        updated_task = self.task.copy()
        updated_task["name"] = self.name_entry.get()

        if self.deadline_var.get() == 0:
            updated_task["deadline"] = "無"
        else:
            updated_task["deadline"] = f"{self.year_combobox.get()}-{self.month_combobox.get()}-{self.day_combobox.get()}-{self.hour_combobox.get()}"

        new_priority = self.priority_combobox.get()
        updated_task["priority"] = new_priority
        new_status = self.status_combobox.get()
        updated_task["status"] = new_status
        new_group = self.group_combobox.get()
        updated_task["group"] = new_group

        # 強制更新 self.parent.tasks 中的資料
        for index, task in enumerate(self.parent.tasks):
            if task.get("id") == updated_task.get("id"):
                self.parent.tasks[index].update(updated_task)
                break

        # 更新 .json 檔案
        self.parent.update_task_in_json(updated_task)

        # 檢查目前的篩選狀態
        current_priority_filter = self.parent.current_filter.get("priority")
        current_group_filter = self.parent.current_filter.get("group")
        current_status_filter = self.parent.current_filter.get("status")

        remove_task = False

        # 檢查狀態變更是否需要移除
        if current_status_filter == "已完成" and new_status != "已完成":
            remove_task = True
        elif current_status_filter != "已完成" and new_status == "已完成":
            remove_task = True
        elif current_status_filter == "展示所有未完成任務" and new_status == "已完成":
            remove_task = True
        elif current_status_filter != "展示所有未完成任務" and current_status_filter is not None and current_status_filter != new_status:
            # 如果有特定的狀態篩選，且新狀態與篩選狀態不同，則移除
            remove_task = True

        # 檢查優先級變更是否需要移除
        if current_priority_filter is not None and current_priority_filter != new_priority:
            remove_task = True

        # 檢查群組變更是否需要移除
        if current_group_filter is not None and current_group_filter != new_group:
            remove_task = True

        if remove_task:
            self.parent.remove_task_from_treeview(updated_task["id"])
        else:
            self.parent.update_task_list() # 在其他情況下，更新 Treeview 顯示

        self.top.destroy()

    def set_default_deadline(self):
        """設定預設截止時間為當下時間"""
        now = datetime.now()
        self.year_combobox.set(str(now.year))
        self.month_combobox.set(f"{now.month:02}")
        self.day_combobox.set(f"{now.day:02}")
        self.hour_combobox.set(f"{now.hour:02}:00")

    def toggle_deadline_fields(self):
        """切換截止日期欄位的啟用狀態"""
        if self.deadline_var.get() == 0:
            self.year_combobox.config(state="disabled")
            self.month_combobox.config(state="disabled")
            self.day_combobox.config(state="disabled")
            self.hour_combobox.config(state="disabled")
        else:
            self.year_combobox.config(state="readonly")
            self.month_combobox.config(state="readonly")
            self.day_combobox.config(state="readonly")
            self.hour_combobox.config(state="readonly")

class ProgressTrackingWindow: #已整理完成
    '''任務管理器的任務記錄功能'''
    #-------------------------------------------------------------------------------------------------------------   
    def __init__(self, parent, task, update_task_in_json_callback):
            self.top = tk.Toplevel(parent)
            self.top.title("任務記錄")
            self.top.geometry("240x350")

            # 阻止視窗被縮放
            self.top.resizable(False, False)

            # 設置為 parent 的暫態子視窗
            self.top.transient(parent)

            # 強制使用者與此視窗互動
            self.top.grab_set()

            self.task = task
            self.update_task_in_json_callback = update_task_in_json_callback

            self.record_label = tk.Label(self.top, text="載入記錄：")
            self.record_label.grid(row=0, column=0, pady=5, sticky="w")

            self.record_combobox = ttk.Combobox(self.top, state="readonly", width=20)
            self.record_combobox.grid(row=0, column=1, pady=5, sticky="w")
            self.record_combobox.bind("<<ComboboxSelected>>", self.display_selected_record)
            self.record_combobox.set("選取記錄")  # 設定預設顯示文字

            self.tracking_date_label = tk.Label(self.top, text="標題：")
            self.tracking_date_label.grid(row=1, column=0, padx=3, pady=5, sticky="w")
            self.tracking_date_entry = tk.Entry(self.top, width=20)
            self.tracking_date_entry.grid(row=1, column=1, padx=3, pady=5, sticky="w")

            self.progress_label = tk.Label(self.top, text="記錄內容：")
            self.progress_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

            # 創建包含 Text 和 Scrollbar 的 Frame
            self.progress_frame = tk.Frame(self.top)
            self.progress_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

            # 先創建 Text widget
            self.progress_text = tk.Text(self.progress_frame, height=15, width=20)
            self.progress_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # 然後創建 Scrollbar
            self.progress_scrollbar = tk.Scrollbar(self.progress_frame, command=self.progress_text.yview)
            self.progress_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # 最後配置 Text widget 的 yscrollcommand
            self.progress_text.config(yscrollcommand=self.progress_scrollbar.set)

            # 按鈕區域
            button_frame = tk.Frame(self.top)
            self.add_button = tk.Button(button_frame, text="新增記錄", command=self.add_new_record)
            self.add_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            self.save_button = tk.Button(button_frame, text="保存", command=self.save_progress)
            self.save_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.remove_button = tk.Button(button_frame, text="移除記錄", command=self.remove_selected_record, state=tk.DISABLED)
            self.remove_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

            button_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
            button_frame.columnconfigure(0, weight=1)
            button_frame.columnconfigure(1, weight=1)
            button_frame.columnconfigure(2, weight=1)

            # 填充已有的記錄
            self.load_progress_data()

            # 配置 row 和 column 的 weight，確保 progress_frame 可以擴展
            self.top.grid_rowconfigure(3, weight=1)
            self.top.grid_columnconfigure(0, weight=1)
            self.top.grid_columnconfigure(1, weight=1)

            # 確保彈出框在父視窗之前
            self.top.lift(parent)

            # 程式執行停留在這個彈出框，直到它被關閉
            self.top.wait_window(self.top)
    #-------------------------------------------------------------------------------------------------------------
    def add_new_record(self):
        """清除輸入框，準備新增一條新記錄"""
        self.tracking_date_entry.delete(0, tk.END)
        self.progress_text.delete("1.0", tk.END)
        self.record_combobox.set("")

    def display_selected_record(self, event=None):
        """顯示選擇的任務記錄"""
        selected_title = self.record_combobox.get()
        if selected_title and selected_title != "點擊載入記錄" and selected_title != "沒有記錄":
            selected_record = next((entry for entry in self.task["progress_tracking"] if entry.get("title") == selected_title), None)
            if selected_record:
                self.progress_text.delete("1.0", tk.END)
                self.progress_text.insert("1.0", selected_record.get("record", ""))
                self.tracking_date_entry.delete(0, tk.END)
                self.tracking_date_entry.insert(0, selected_record.get("title", ""))
        elif not selected_title or selected_title == "點擊載入記錄" or selected_title == "沒有記錄":
            self.progress_text.delete("1.0", tk.END)
            self.tracking_date_entry.delete(0, tk.END)

    def load_progress_data(self):
        """載入記錄資料，並按標題 A-Z 排序，預設顯示提示文字並控制移除按鈕狀態"""
        has_records = "progress_tracking" in self.task and len(self.task["progress_tracking"]) > 0

        if has_records:
            record_titles = [entry.get("title", "") for entry in self.task["progress_tracking"]]
            record_titles.sort()
            self.record_combobox['values'] = record_titles
            if not self.record_combobox.get(): # 只有在 ComboBox 為空時才設定提示文字
                self.record_combobox.set("點擊載入記錄")
            self.remove_button.config(state=tk.NORMAL)  # 啟用移除按鈕
        else:
            self.progress_text.delete("1.0", tk.END)
            self.tracking_date_entry.delete(0, tk.END)
            self.record_combobox['values'] = []
            self.record_combobox.set("沒有記錄")
            self.remove_button.config(state=tk.DISABLED)  # 確保沒有記錄時禁用

    def remove_selected_record(self):
        """移除選取的任務記錄，並在移除前顯示確認對話框"""
        selected_title = self.record_combobox.get()
        if selected_title and selected_title != "點擊載入記錄" and selected_title != "沒有記錄":
            if messagebox.askyesno("確認", f"此操作無法復原，是否確定要移除記錄 '{selected_title}'？"):
                index_to_remove = -1
                for i, entry in enumerate(self.task["progress_tracking"]):
                    if entry.get("title") == selected_title:
                        index_to_remove = i
                        break

                if index_to_remove != -1:
                    del self.task["progress_tracking"][index_to_remove]
                    self.load_progress_data()  # 重新載入下拉選單
                    self.progress_text.delete("1.0", tk.END)
                    self.tracking_date_entry.delete(0, tk.END)
                    self.update_task_in_json_callback(self.task)
                    messagebox.showinfo("訊息", f"記錄 '{selected_title}' 已移除。")
                else:
                    messagebox.showerror("錯誤", f"找不到標題為 '{selected_title}' 的記錄。")
        elif selected_title == "點擊載入記錄" or selected_title == "沒有記錄":
            messagebox.showinfo("提示", "請先選擇要移除的記錄。")
        else:
            messagebox.showinfo("提示", "請先選擇要移除的記錄。")

    def save_progress(self):
        """保存進度記錄，使用日期作為唯一識別符"""
        progress = self.progress_text.get("1.0", tk.END).strip()
        tracking_date = self.tracking_date_entry.get().strip()

        if progress and tracking_date:
            if "progress_tracking" not in self.task:
                self.task["progress_tracking"] = []

            # 檢查任務記錄是否已經存在
            existing_record = next((entry for entry in self.task["progress_tracking"] if entry["title"] == tracking_date), None)
            if existing_record:
                # 如果已經此title的進度紀錄，更新它
                existing_record["record"] = progress 
            else:
                # 否則新增一條新的進度紀錄
                self.task["progress_tracking"].append({"title": tracking_date, "record": progress})

            self.load_progress_data()  # 刷新下拉選單
            self.update_task_in_json_callback(self.task)
            self.tracking_date_entry.delete(0, tk.END)
            self.progress_text.delete("1.0", tk.END)
        else:
            messagebox.showwarning("警告", "記錄日期與內容必須填寫!")