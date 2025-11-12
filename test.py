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
            if price < 0 or quantity <= 0:
                messagebox.showwarning("입력 오류", "가격은 0 이상, 수량은 1 이상이어야 합니다.", parent=self)
                return
            self.result = (price, quantity)
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

        self.random_colors = self.generate_random_colors(3)
        self.selected_color = tk.StringVar()
        self.color_buttons = []

        body = tk.Frame(self)
        tk.Label(body, text="구입할 색상 하나를 선택하세요.").pack(pady=10)
        
        button_frame = tk.Frame(body)
        button_frame.pack(pady=5)

        for color in self.random_colors:
            rb = tk.Radiobutton(
                button_frame, 
                text=color, 
                variable=self.selected_color, 
                value=color,
                indicatoron=0, # 라디오 버튼의 원 모양을 숨깁니다.
                width=10,
                bg=color,
                selectcolor=color, # 선택되었을 때 배경색
                command=self.on_color_select
            )
            rb.pack(side="left", padx=5)

        body.pack(padx=15, pady=15)

        self.add_button = tk.Button(self, text="팔레트에 추가", command=self.add_color_to_palette, state="disabled")
        self.add_button.pack(pady=10)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry(f"+{parent.root.winfo_rootx()+100}+{parent.root.winfo_rooty()+100}")
        self.wait_window(self)

    def generate_random_colors(self, count):
        """지정된 개수만큼 랜덤 hex 색상 코드를 생성합니다."""
        return [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(count)]

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
        self.no_paper_warning_shown = False # 종이 부족 경고를 한 번만 표시하기 위한 플래그

        # --- 사용자 잔액 ---
        self.balance = 10000
        self.balance_var = tk.StringVar()
        self.balance_var.set(f"내 잔액: {self.balance:,}원")

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
        business_menu.add_command(label="영업중")
        business_menu.add_command(label="영업 중지")

        # '상점' 메뉴 생성
        shop_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="상점", menu=shop_menu)
        shop_menu.add_command(label="종이 추가", command=self.add_paper)
        shop_menu.add_command(label="물감 구입", command=self.open_paint_shop)

    def create_layout(self):
        # 1. 왼쪽 프레임 (픽셀 아트 캔버스 영역)
        canvas_frame = tk.Frame(self.root, bd=2, relief="sunken", padx=10, pady=10)
        canvas_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        canvas_label = tk.Label(canvas_frame, text="<< 픽셀 아트를 그릴 격자 캔버스 >>", font=("Arial", 14))
        canvas_label.pack(pady=10)

        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=0)
        self.canvas.pack()
        self.draw_grid()

        self.canvas.bind("<B1-Motion>", self.paint_cell)
        self.canvas.bind("<Button-1>", self.paint_cell)
        self.canvas.bind("<B3-Motion>", self.erase_cell)
        self.canvas.bind("<Button-3>", self.erase_cell)

        # --- 컨트롤 프레임 (색상 팔레트, 버튼) ---
        controls_frame = tk.Frame(canvas_frame)
        controls_frame.pack(pady=10)
        
        self.palette_frame = tk.Frame(controls_frame) # 색상 버튼을 담을 프레임
        self.palette_frame.pack(side="left")

        initial_colors = ["black", "red", "blue", "green"]
        self.add_new_colors(initial_colors) # 초기 색상 팔레트 생성

        clear_btn = tk.Button(controls_frame, text="모두 지우기", command=self.clear_canvas)
        clear_btn.pack(side="left", padx=20)

        # '자판기에 등록하기' 버튼 추가
        register_btn = tk.Button(controls_frame, text="자판기에 등록하기", command=self.register_art)
        register_btn.pack(side="left", padx=5)

        # 남은 종이 라벨 추가
        paper_label = tk.Label(controls_frame, textvariable=self.paper_count_var, font=("Arial", 10))
        paper_label.pack(side="left", padx=20)

        # 2. 오른쪽 프레임 (탭 인터페이스 영역)
        right_frame = tk.Frame(self.root, bd=2, relief="sunken")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # 잔액 및 충전 프레임 (탭 바깥에 위치)
        top_info_frame = tk.Frame(right_frame)
        top_info_frame.pack(pady=10, fill="x")

        balance_label = tk.Label(top_info_frame, textvariable=self.balance_var, font=("Arial", 12, "bold"))
        balance_label.pack()

        charge_frame = tk.Frame(top_info_frame)
        charge_frame.pack()
        self.charge_entry = tk.Entry(charge_frame, width=15)
        self.charge_entry.pack(side="left", padx=5)
        charge_button = tk.Button(charge_frame, text="충전하기", command=self.charge_balance)
        charge_button.pack(side="left")

        # --- 탭 생성 ---
        notebook = ttk.Notebook(right_frame)
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
        random_draw_button = tk.Button(draw_frame, text="랜덤 뽑기 (300원)", command=self.random_draw)
        random_draw_button.pack()

        self.scrollable_gallery_frame = self.create_scrollable_frame(gallery_content_frame)

        # '내 컬렉션' 탭
        collection_tab = tk.Frame(notebook)
        notebook.add(collection_tab, text="내 컬렉션")
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
        self.change_cell_color(event, self.current_color)

    def erase_cell(self, event):
        self.change_cell_color(event, "white")

    def change_cell_color(self, event, color):
        # 종이가 없으면 그리기를 막습니다.
        if self.paper_count < 1:
            if not self.no_paper_warning_shown:
                messagebox.showwarning("종이 부족", "종이가 없어 그림을 그릴 수 없습니다.\n상점에서 종이를 추가해주세요.", parent=self.root)
                self.no_paper_warning_shown = True # 경고를 표시했음을 기록
            return

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

    def register_art(self):
        # 종이가 있는지 확인
        if self.paper_count < 1:
            messagebox.showwarning("종이 부족", "남은 종이가 없습니다. 상점에서 종이를 추가하세요.", parent=self.root)
            return

        # 등록 다이얼로그 실행
        dialog = RegisterDialog(self.root)
        result = dialog.result

        if result:
            price, quantity = result
            try:
                self.art_counter += 1
                filename = f"art_{self.art_counter:02d}.png"
                filepath = os.path.join(self.art_dir, filename)
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
            self.no_paper_warning_shown = False # 종이가 추가되었으므로 경고 플래그 리셋
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
            
            price_text = f"가격: {item['price']:,}원"
            stock_text = f"재고: {item['stock']}개"
            price_label = tk.Label(info_frame, text=price_text, font=("Arial", 12))
            price_label.pack(anchor="w")
            stock_label = tk.Label(info_frame, text=stock_text, font=("Arial", 10))
            stock_label.pack(anchor="w")

            buy_button = tk.Button(info_frame)
            buy_button.pack(anchor="w", pady=5)
            
            if item['stock'] <= 0:
                buy_button.config(text="품절", state="disabled")
            else:
                buy_button.config(text="구입", command=lambda i=item, sl=stock_label, btn=buy_button: self.buy_art(i, sl, btn))

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


if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtVendingMachine(root)
    root.mainloop()