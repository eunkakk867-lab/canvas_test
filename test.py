import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageTk
import os
import random

class RegisterDialog(tk.Toplevel):
    """가격과 수량을 입력받기 위한 커스텀 대화상자"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.transient(parent)
        self.title("그림 등록")

        self.result = None

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=15, pady=15)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry(f"+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")
        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self, master):
        tk.Label(master, text="가격:").grid(row=0, column=0, sticky="w", pady=2)
        self.price_entry = tk.Entry(master)
        self.price_entry.grid(row=0, column=1)

        tk.Label(master, text="판매 수량:").grid(row=1, column=0, sticky="w", pady=2)
        self.quantity_entry = tk.Entry(master)
        self.quantity_entry.grid(row=1, column=1)
        
        tk.Label(master, text="파일 이름:").grid(row=2, column=0, sticky="w", pady=2)
        self.filename_entry = tk.Entry(master)
        self.filename_entry.grid(row=2, column=1)

        return self.price_entry

    def buttonbox(self):
        box = tk.Frame(self)
        w = tk.Button(box, text="확인", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="취소", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def ok(self, event=None):
        try:
            price = int(self.price_entry.get())
            quantity = int(self.quantity_entry.get())
            filename = self.filename_entry.get().strip()

            if price < 0 or quantity <= 0:
                messagebox.showwarning("입력 오류", "가격은 0 이상, 수량은 1 이상이어야 합니다.", parent=self)
                return
            
            if not filename:
                messagebox.showwarning("입력 오류", "파일 이름을 입력해야 합니다.", parent=self)
                return

            self.result = (price, quantity, filename)
            self.cancel()
        except ValueError:
            messagebox.showwarning("입력 오류", "가격과 수량은 숫자로 입력해야 합니다.", parent=self)

    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()

class PaintShopDialog(tk.Toplevel):
    """새로운 물감(색상)을 구입하기 위한 커스텀 대화상자"""
    def __init__(self, parent):
        # parent는 이제 PixelArtVendingMachine 인스턴스입니다.
        super().__init__(parent.root)
        self.parent_app = parent
        self.transient(parent.root)
        self.title("물감 구입")

        # 지정된 색상 목록에서 3개를 랜덤으로 선택
        color_pool = ["orange", "yellow", "skyblue", "pink", "purple", "white"]
        # 기존 팔레트에 없는 색상만 필터링
        existing_colors = [btn.cget('bg') for btn in self.parent_app.palette_frame.winfo_children()]
        new_color_pool = [c for c in color_pool if c not in existing_colors]
        
        # 선택할 색상이 3개 미만이면 있는 만큼만, 없으면 빈 리스트
        self.random_colors = random.sample(new_color_pool, min(len(new_color_pool), 3))

        self.selected_color = tk.StringVar()
        
        body = tk.Frame(self)
        tk.Label(body, text="구입할 색상 하나를 선택하세요.").pack(pady=10)
        
        button_frame = tk.Frame(body)
        button_frame.pack(pady=5)

        for color in self.random_colors:
            # Radiobutton 텍스트를 비워서 색상만 보이게 함
            rb = tk.Radiobutton(button_frame, 
                                text="", 
                                variable=self.selected_color, 
                                value=color,
                                indicatoron=0,
                                width=10,
                                bg=color,
                                selectcolor=color,
                                command=self.on_color_select)
            rb.pack(side="left", padx=5)

        body.pack(padx=15, pady=15)

        if not self.random_colors:
            tk.Label(body, text="추가할 수 있는 새 물감이 없습니다.").pack(pady=5)

        self.add_button = tk.Button(self, text="팔레트에 추가", command=self.add_color_to_palette, state="disabled")
        self.add_button.pack(pady=10)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry(f"+{parent.root.winfo_rootx()+100}+{parent.root.winfo_rooty()+100}")
        self.wait_window(self)

    def on_color_select(self):
        """색상이 선택되면 '추가' 버튼을 활성화합니다."""
        if self.selected_color.get():
            self.add_button.config(state="normal")

    def add_color_to_palette(self):
        """선택된 색상을 메인 팔레트에 추가합니다."""
        color = self.selected_color.get()
        if color:
            self.parent_app.add_new_colors([color])
        self.destroy()

    def cancel(self):
        self.destroy()

class PixelArtVendingMachine:
    def __init__(self, root):
        self.root = root
        self.root.title("픽셀 아트 판매 자판기")
        self.root.geometry("1000x700")

        self.create_menubar() # 메뉴바 생성

        # --- 캔버스 설정 ---
        self.grid_size = 20
        self.cell_size = 25
        self.canvas_width = self.grid_size * self.cell_size
        self.canvas_height = self.grid_size * self.cell_size
        
        self.grid_cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # --- 그리기 도구 설정 ---
        self.current_color = "black"

        # --- 자판기 데이터 ---
        self.vending_machine_items = [] # 등록된 아트 정보 (파일명, 가격, 재고) 저장
        self.art_counter = 0 # 파일명 중복 방지를 위한 카운터
        self.art_dir = "arts" # 이미지를 저장할 디렉토리
        if not os.path.exists(self.art_dir):
            os.makedirs(self.art_dir)
        
        # --- 재료 데이터 ---
        self.paper_count = 0
        self.paper_count_var = tk.StringVar()
        self.paper_count_var.set(f"남은 종이: {self.paper_count}장")

        # --- 사용자 잔액 ---
        self.balance = 10000
        self.balance_var = tk.StringVar()
        self.balance_var.set(f"내 잔액: {self.balance:,}원")

        # --- 영업 상태 ---
        self.is_business_open = True
        self.status_var = tk.StringVar()
        self.status_var.set("현재 상태: 영업중")

        # --- UI 위젯 저장 ---
        self.background_widgets = [] # 배경색 변경 대상 위젯 리스트

        # --- 갤러리/컬렉션 위젯 ---
        self.gallery_images = [] # 갤러리 탭용 PhotoImage 리스트
        self.my_collection = [] # 내가 구매한 아이템 목록
        self.collection_images = [] # 컬렉션 탭용 PhotoImage 리스트

        self.create_layout()
        self.update_gallery() # 초기 갤러리 로딩
        self.update_collection() # 초기 컬렉션 로딩

    def create_menubar(self):
        """애플리케이션의 메인 메뉴바를 생성합니다."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # '영업' 메뉴 생성
        business_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="영업", menu=business_menu)
        business_menu.add_command(label="영업중", command=self.start_business)
        business_menu.add_command(label="영업 중지", command=self.stop_business)

        # '상점' 메뉴 생성
        shop_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="상점", menu=shop_menu)
        shop_menu.add_command(label="종이 추가", command=self.add_paper)
        shop_menu.add_command(label="물감 구입", command=self.open_paint_shop)
    
    def create_layout(self):
        # 최상단 프레임 (상태 라벨)
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side="top", fill="x", padx=10, pady=(5, 0))

        self.status_label = tk.Label(self.top_frame, textvariable=self.status_var, font=("Arial", 12, "bold"), fg="green")
        self.status_label.pack()

        # 메인 컨텐츠 프레임
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # 배경색 변경 대상 위젯 추가
        self.background_widgets.extend([self.root, self.top_frame, self.status_label, self.main_frame])

        # 1. 왼쪽 프레임 (픽셀 아트 캔버스 영역)
        self.canvas_frame = tk.Frame(self.main_frame, bd=2, relief="sunken", padx=10, pady=10)
        self.canvas_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        canvas_label = tk.Label(self.canvas_frame, text="<< 픽셀 아트를 그릴 격자 캔버스 >>", font=("Arial", 14))
        canvas_label.pack(pady=10)

        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=0)
        self.canvas.pack()
        self.draw_grid()

        self.canvas.bind("<B1-Motion>", self.paint_cell)
        self.canvas.bind("<ButtonPress-1>", self.handle_canvas_press)
        self.canvas.bind("<B3-Motion>", self.erase_cell)
        self.canvas.bind("<ButtonPress-3>", self.handle_canvas_press)

        # --- 컨트롤 프레임 (색상 팔레트, 버튼) ---
        self.controls_frame = tk.Frame(self.canvas_frame)
        self.controls_frame.pack(pady=10)
        
        self.palette_frame = tk.Frame(self.controls_frame) # 색상 버튼을 담을 프레임
        self.palette_frame.pack(side="left")

        initial_colors = ["black", "red", "blue", "green"]
        self.add_new_colors(initial_colors) # 초기 색상 팔레트 생성

        self.clear_btn = tk.Button(self.controls_frame, text="모두 지우기", command=self.clear_canvas)
        self.clear_btn.pack(side="left", padx=20)

        # '자판기에 등록하기' 버튼 추가
        self.register_btn = tk.Button(self.controls_frame, text="자판기에 등록하기", command=self.register_art)
        self.register_btn.pack(side="left", padx=5)

        # 남은 종이 라벨 추가
        paper_label = tk.Label(self.controls_frame, textvariable=self.paper_count_var, font=("Arial", 10))
        paper_label.pack(side="left", padx=20)

        # 2. 오른쪽 프레임 (탭 인터페이스 영역)
        self.right_frame = tk.Frame(self.main_frame, bd=2, relief="sunken")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # 잔액 및 충전 프레임 (탭 바깥에 위치)
        self.top_info_frame = tk.Frame(self.right_frame)
        self.top_info_frame.pack(pady=10, fill="x")

        balance_label = tk.Label(self.top_info_frame, textvariable=self.balance_var, font=("Arial", 12, "bold"))
        balance_label.pack()

        self.charge_frame = tk.Frame(self.top_info_frame)
        self.charge_frame.pack()
        self.charge_entry = tk.Entry(self.charge_frame, width=15)
        self.charge_entry.pack(side="left", padx=5)
        self.charge_button = tk.Button(self.charge_frame, text="충전하기", command=self.charge_balance)
        self.charge_button.pack(side="left")

        self.background_widgets.extend([self.canvas_frame, canvas_label, self.controls_frame, self.right_frame, self.top_info_frame, balance_label, self.charge_frame, paper_label])

        # --- 탭 생성 ---
        notebook = ttk.Notebook(self.right_frame)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # '자판기 갤러리' 탭
        gallery_tab = tk.Frame(notebook)
        notebook.add(gallery_tab, text="자판기 갤러리")        
        
        # 갤러리 탭 내의 컨텐츠 프레임
        gallery_content_frame = tk.Frame(gallery_tab)
        gallery_content_frame.pack(fill="both", expand=True)

        # 랜덤 뽑기 버튼 프레임
        draw_frame = tk.Frame(gallery_content_frame)
        draw_frame.pack(pady=5)
        self.random_draw_button = tk.Button(draw_frame, text="랜덤 뽑기 (300원)", command=self.random_draw)
        self.random_draw_button.pack()

        self.scrollable_gallery_frame = self.create_scrollable_frame(gallery_content_frame)

        # '내 컬렉션' 탭
        collection_tab = tk.Frame(notebook)
        notebook.add(collection_tab, text="내 컬렉션")

        self.background_widgets.extend([gallery_tab, gallery_content_frame, draw_frame, collection_tab])
        self.scrollable_collection_frame = self.create_scrollable_frame(collection_tab)

    def create_scrollable_frame(self, parent_tab):
        """스크롤 가능한 프레임을 생성하여 반환하는 헬퍼 함수"""
        scrollbar = tk.Scrollbar(parent_tab)
        scrollbar.pack(side="right", fill="y")
        canvas = tk.Canvas(parent_tab, yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        return scrollable_frame

    def draw_grid(self):
        for i in range(self.grid_size + 1):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.canvas_height, fill="lightgrey")
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.canvas_width, y, fill="lightgrey")

    def paint_cell(self, event):
        # 종이가 없으면 그리기 동작을 막습니다.
        if self.paper_count < 1:
            return
        self.change_cell_color(event, self.current_color)

    def erase_cell(self, event):
        # 종이가 없으면 지우기 동작을 막습니다.
        if self.paper_count < 1:
            return
        self.change_cell_color(event, "white")

    def change_cell_color(self, event, color):
        # 캔버스 범위 내에서만 그리도록 제한
        if 0 <= event.x < self.canvas_width and 0 <= event.y < self.canvas_height:
            col = event.x // self.cell_size
            row = event.y // self.cell_size
            if self.grid_cells[row][col]:
                self.canvas.delete(self.grid_cells[row][col])
            if color != "white":
                x1, y1 = col * self.cell_size, row * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                self.grid_cells[row][col] = rect_id
            else:
                self.grid_cells[row][col] = None
    
    def handle_canvas_press(self, event):
        """캔버스 클릭 시 종이 유무를 확인하고, 그리기/지우기를 실행합니다."""
        if self.paper_count < 1:
            messagebox.showwarning("종이 부족", "종이가 없어 그림을 그릴 수 없습니다.\n상점에서 종이를 추가해주세요.", parent=self.root)
            return
        
        if event.num == 1: # 마우스 왼쪽 버튼
            self.paint_cell(event)
        elif event.num == 3: # 마우스 오른쪽 버튼
            self.erase_cell(event)

    def select_color(self, new_color):
        self.current_color = new_color

    def clear_canvas(self):
        # 종이가 없으면 지우기를 막습니다.
        if self.paper_count < 1:
            messagebox.showwarning("종이 부족", "종이가 없어 캔버스를 지울 수 없습니다.", parent=self.root)
            return

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid_cells[row][col]:
                    self.canvas.delete(self.grid_cells[row][col])
                    self.grid_cells[row][col] = None

    def redraw_canvas(self):
        """grid_cells 데이터 기준으로 캔버스를 다시 그립니다."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell_id = self.grid_cells[row][col]
                if cell_id:
                    color = self.canvas.itemcget(cell_id, "fill")
                    x1, y1 = col * self.cell_size, row * self.cell_size
                    x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                    new_rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                    self.grid_cells[row][col] = new_rect_id # 새 ID로 업데이트

    def register_art(self):
        # 종이가 있는지 확인
        if self.paper_count < 1:
            messagebox.showwarning("종이 부족", "남은 종이가 없습니다. 상점에서 종이를 추가하세요.", parent=self.root)
            return

        # 등록 다이얼로그 실행
        dialog = RegisterDialog(self.root)
        result = dialog.result

        if result:
            price, quantity, filename = result
            try:
                # 파일 이름에 .png 확장자가 없으면 추가
                if not filename.lower().endswith('.png'):
                    filename += '.png'

                filepath = os.path.join(self.art_dir, filename)
                if os.path.exists(filepath):
                    if not messagebox.askyesno("파일 덮어쓰기", "같은 이름의 파일이 이미 존재합니다. 덮어쓰시겠습니까?", parent=self.root):
                        return

                image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
                draw = ImageDraw.Draw(image)
                for row in range(self.grid_size):
                    for col in range(self.grid_size):
                        if self.grid_cells[row][col]:
                            color = self.canvas.itemcget(self.grid_cells[row][col], "fill")
                            x1, y1 = col * self.cell_size, row * self.cell_size
                            x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                            draw.rectangle([x1, y1, x2, y2], fill=color)
                image.save(filepath)
                art_info = {"filepath": filepath, "price": price, "stock": quantity}
                self.vending_machine_items.append(art_info)
                messagebox.showinfo("등록 완료", f"'{filename}'으로 저장되었습니다.\n가격: {price}원, 수량: {quantity}개")

                # 등록 성공 시 종이 1장 차감
                self.paper_count -= 1
                self.paper_count_var.set(f"남은 종이: {self.paper_count}장")

                self.update_gallery()
            except Exception as e:
                messagebox.showerror("오류", f"이미지 저장 중 오류가 발생했습니다:\n{e}")

    def add_paper(self):
        """'종이 추가' 메뉴를 통해 종이를 추가합니다."""
        num_to_add = simpledialog.askinteger("종이 추가", "몇 장을 추가하시겠습니까?", parent=self.root, minvalue=1)
        if num_to_add:
            self.paper_count += num_to_add
            self.paper_count_var.set(f"남은 종이: {self.paper_count}장")
            messagebox.showinfo("완료", f"{num_to_add}장의 종이를 추가했습니다.", parent=self.root)

    def open_paint_shop(self):
        """'물감 구입' 팝업창을 엽니다."""
        PaintShopDialog(self) # self(PixelArtVendingMachine 인스턴스)를 전달

    def add_new_colors(self, colors):
        """색상 팔레트에 새로운 색상 버튼들을 추가합니다."""
        for color in colors:
            if color: # None이 아닌 유효한 색상만 추가
                color_btn = tk.Button(
                    self.palette_frame, 
                    bg=color, 
                    width=4, 
                    command=lambda c=color: self.select_color(c)
                )
                color_btn.pack(side="left", padx=2)

    def update_gallery(self):
        for widget in self.scrollable_gallery_frame.winfo_children():
            widget.destroy()
        self.gallery_images.clear()
        self.gallery_buy_buttons = [] # 구입 버튼 목록 초기화
        for item in self.vending_machine_items:
            item_frame = tk.Frame(self.scrollable_gallery_frame, bd=1, relief="solid")
            item_frame.pack(pady=5, padx=10, fill="x")
            img = Image.open(item["filepath"])
            img.thumbnail((100, 100))
            photo_img = ImageTk.PhotoImage(img)
            self.gallery_images.append(photo_img)
            img_label = tk.Label(item_frame, image=photo_img)
            img_label.pack(side="left", padx=5, pady=5)
            info_frame = tk.Frame(item_frame)
            info_frame.pack(side="left", padx=10)
            
            filename = os.path.basename(item["filepath"])
            filename_label = tk.Label(info_frame, text=filename, font=("Arial", 12, "bold"))
            filename_label.pack(anchor="w")

            price_text = f"가격: {item['price']:,}원"
            stock_text = f"재고: {item['stock']}개"
            price_label = tk.Label(info_frame, text=price_text, font=("Arial", 10))
            price_label.pack(anchor="w")
            stock_label = tk.Label(info_frame, text=stock_text, font=("Arial", 9))
            stock_label.pack(anchor="w")

            buy_button = tk.Button(info_frame)
            buy_button.pack(anchor="w", pady=5)
            self.gallery_buy_buttons.append(buy_button) # 버튼 목록에 추가
            
            if item['stock'] <= 0:
                buy_button.config(text="품절", state="disabled")
            else:
                buy_button.config(text="구입", command=lambda i=item, sl=stock_label, btn=buy_button: self.buy_art(i, sl, btn))
            
            if not self.is_business_open:
                buy_button.config(state="disabled")

    def update_collection(self):
        """'내 컬렉션' 탭을 업데이트합니다."""
        for widget in self.scrollable_collection_frame.winfo_children():
            widget.destroy()
        self.collection_images.clear()
        
        for item_path, count in self.my_collection:
            item_frame = tk.Frame(self.scrollable_collection_frame, bd=1, relief="solid")
            item_frame.pack(pady=5, padx=10, fill="x")
            img = Image.open(item_path)
            img.thumbnail((100, 100))
            photo_img = ImageTk.PhotoImage(img)
            self.collection_images.append(photo_img)
            img_label = tk.Label(item_frame, image=photo_img)
            img_label.pack(side="left", padx=5, pady=5)
            
            info_frame = tk.Frame(item_frame)
            info_frame.pack(side="left", padx=10)
            
            filename_label = tk.Label(info_frame, text=os.path.basename(item_path), font=("Arial", 10))
            filename_label.pack(anchor="w")
            count_label = tk.Label(info_frame, text=f"보유 수량: {count}개", font=("Arial", 10, "bold"))
            count_label.pack(anchor="w")

    def buy_art(self, item, stock_label, button):
        price = item["price"]
        if self.balance >= price:
            self.balance -= price
            self.balance_var.set(f"내 잔액: {self.balance:,}원")
            
            item["stock"] -= 1
            stock_label.config(text=f"재고: {item['stock']}개")

            # 내 컬렉션에 추가 또는 수량 증가
            found = False
            for i, (path, count) in enumerate(self.my_collection):
                if path == item["filepath"]:
                    self.my_collection[i] = (path, count + 1)
                    found = True
                    break
            if not found:
                self.my_collection.append((item["filepath"], 1))

            if item["stock"] <= 0:
                button.config(text="품절", state="disabled")

            messagebox.showinfo("구매 완료", "그림을 성공적으로 구매했습니다!")
            self.update_collection() # 구매 성공 시 컬렉션 탭 업데이트
        else:
            messagebox.showwarning("잔액 부족", "잔액이 부족하여 그림을 구매할 수 없습니다.")

    def charge_balance(self):
        try:
            amount_str = self.charge_entry.get()
            if not amount_str:
                return

            amount = int(amount_str)
            if amount > 0:
                self.balance += amount
                self.balance_var.set(f"내 잔액: {self.balance:,}원")
                self.charge_entry.delete(0, 'end')
            else:
                messagebox.showwarning("입력 오류", "0보다 큰 금액을 입력해주세요.")
                self.charge_entry.delete(0, 'end')
        except ValueError:
            messagebox.showerror("입력 오류", "숫자만 입력해주세요.")
            self.charge_entry.delete(0, 'end')

    def random_draw(self):
        """300원으로 무작위 아이템을 뽑습니다."""
        draw_price = 300
        
        # 재고가 있는 아이템 목록 필터링
        available_items = [item for item in self.vending_machine_items if item['stock'] > 0]

        if not available_items:
            messagebox.showinfo("품절", "뽑을 수 있는 그림이 없습니다.")
            return

        if self.balance < draw_price:
            messagebox.showwarning("잔액 부족", f"뽑기를 위한 잔액이 부족합니다. ({draw_price}원 필요)")
            return

        # 잔액 차감
        self.balance -= draw_price
        self.balance_var.set(f"내 잔액: {self.balance:,}원")

        # 랜덤 아이템 선택
        drawn_item = random.choice(available_items)
        
        # 재고 차감
        drawn_item["stock"] -= 1

        # 내 컬렉션에 추가 또는 수량 증가
        found = False
        for i, (path, count) in enumerate(self.my_collection):
            if path == drawn_item["filepath"]:
                self.my_collection[i] = (path, count + 1)
                found = True
                break
        if not found:
            self.my_collection.append((drawn_item["filepath"], 1))

        # 갤러리 및 컬렉션 UI 업데이트
        self.update_gallery()
        self.update_collection()

        # 성공 메시지 표시
        filename = os.path.basename(drawn_item["filepath"])
        messagebox.showinfo("획득!", f"축하합니다! '{filename}' 그림을 획득했습니다!")

    def stop_business(self):
        """영업을 중지합니다."""
        if not self.is_business_open:
            return
        self.is_business_open = False

        # 상태 라벨 업데이트
        self.status_var.set("현재 상태: 영업 중지")
        self.status_label.config(fg="red")

        # 캔버스 비활성화
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B3-Motion>")
        self.canvas.unbind("<Button-3>")

        # 캔버스 배경 회색으로 변경
        self.canvas.config(bg="#f0f0f0") # 연한 회색
        self.canvas.delete("all") # 기존 그림과 격자 모두 삭제

        # '구입' 버튼 비활성화
        for button in self.gallery_buy_buttons:
            button.config(state="disabled")

        # 주요 기능 버튼 비활성화
        self.random_draw_button.config(state="disabled")
        self.register_btn.config(state="disabled")

        # 배경색 어둡게 변경
        dark_bg = "#e0e0e0"
        for widget in self.background_widgets:
            try:
                widget.config(bg=dark_bg)
            except tk.TclError:
                # 일부 위젯은 bg 속성이 없을 수 있음 (예: ttk.Notebook)
                pass

    def start_business(self):
        """영업을 다시 시작합니다."""
        if self.is_business_open:
            return
        self.is_business_open = True

        # 상태 라벨 업데이트
        self.status_var.set("현재 상태: 영업중")
        self.status_label.config(fg="green")

        # 캔버스 활성화 및 복원
        self.canvas.config(bg="white")
        self.draw_grid() # 격자 다시 그리기
        self.redraw_canvas() # 저장된 그림 다시 그리기
        self.canvas.bind("<B1-Motion>", self.paint_cell)
        self.canvas.bind("<Button-1>", self.paint_cell)
        self.canvas.bind("<B3-Motion>", self.erase_cell) # 이 줄은 handle_canvas_press와 중복될 수 있으나, 드래그를 위해 유지합니다.
        self.canvas.bind("<ButtonPress-3>", self.handle_canvas_press)

        # 주요 기능 버튼 활성화
        self.random_draw_button.config(state="normal")
        self.register_btn.config(state="normal")

        # 갤러리 업데이트 (버튼 상태 복원)
        self.update_gallery()

        # 배경색 원래대로 복원
        default_bg = "#f0f0f0" # Tkinter 기본 배경색
        for widget in self.background_widgets:
            try:
                widget.config(bg=default_bg)
            except tk.TclError:
                pass
        self.status_label.config(bg=default_bg) # 상태 라벨은 별도 처리

if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtVendingMachine(root)
    root.mainloop()