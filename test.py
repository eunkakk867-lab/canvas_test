import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageDraw, ImageTk
import os

class PixelArtVendingMachine:
    def __init__(self, root):
        self.root = root
        self.root.title("픽셀 아트 판매 자판기")
        self.root.geometry("1000x700")

        # --- 캔버스 설정 ---
        self.grid_size = 20
        self.cell_size = 25
        self.canvas_width = self.grid_size * self.cell_size
        self.canvas_height = self.grid_size * self.cell_size
        
        self.grid_cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # --- 그리기 도구 설정 ---
        self.current_color = "black"

        # --- 자판기 데이터 ---
        self.vending_machine_items = [] # 등록된 아트 정보 (파일명, 가격) 저장
        self.art_counter = 0 # 파일명 중복 방지를 위한 카운터
        self.art_dir = "arts" # 이미지를 저장할 디렉토리
        if not os.path.exists(self.art_dir):
            os.makedirs(self.art_dir)
        
        # --- 갤러리 위젯 ---
        self.gallery_images = [] # PhotoImage 객체 가비지 컬렉션 방지용

        self.create_layout()

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

        colors = ["black", "red", "blue", "green"]
        for color in colors:
            color_btn = tk.Button(controls_frame, bg=color, width=4, command=lambda c=color: self.select_color(c))
            color_btn.pack(side="left", padx=5)

        clear_btn = tk.Button(controls_frame, text="모두 지우기", command=self.clear_canvas)
        clear_btn.pack(side="left", padx=20)

        # '자판기에 등록하기' 버튼 추가
        register_btn = tk.Button(controls_frame, text="자판기에 등록하기", command=self.register_art)
        register_btn.pack(side="left", padx=5)

        # 2. 오른쪽 프레임 (자판기 갤러리 영역)
        gallery_outer_frame = tk.Frame(self.root, bd=2, relief="sunken")
        gallery_outer_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        gallery_label = tk.Label(gallery_outer_frame, text="<< 자판기 갤러리 >>", font=("Arial", 14))
        gallery_label.pack(pady=10)

        # 스크롤바와 캔버스를 포함할 프레임
        gallery_content_frame = tk.Frame(gallery_outer_frame)
        gallery_content_frame.pack(fill="both", expand=True)

        # 스크롤바 생성
        scrollbar = tk.Scrollbar(gallery_content_frame)
        scrollbar.pack(side="right", fill="y")

        # 갤러리 아이템을 보여줄 캔버스
        self.gallery_canvas = tk.Canvas(gallery_content_frame, yscrollcommand=scrollbar.set)
        self.gallery_canvas.pack(side="left", fill="both", expand=True)

        # 스크롤바와 캔버스 연결
        scrollbar.config(command=self.gallery_canvas.yview)

        # 캔버스 내부에 실제 위젯들이 들어갈 프레임
        self.scrollable_gallery_frame = tk.Frame(self.gallery_canvas)
        self.gallery_canvas.create_window((0, 0), window=self.scrollable_gallery_frame, anchor="nw")

        # 스크롤 영역 설정
        self.scrollable_gallery_frame.bind(
            "<Configure>",
            lambda e: self.gallery_canvas.configure(scrollregion=self.gallery_canvas.bbox("all"))
        )

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
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid_cells[row][col]:
                    self.canvas.delete(self.grid_cells[row][col])
                    self.grid_cells[row][col] = None

    def register_art(self):
        """팝업으로 가격을 입력받고 캔버스 내용을 이미지로 저장합니다."""
        price = simpledialog.askinteger("가격 설정", "그림 가격을 입력하세요:", parent=self.root, minvalue=0)

        if price is not None: # 사용자가 '취소'를 누르지 않았을 경우
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
                            x1 = col * self.cell_size
                            y1 = row * self.cell_size
                            x2 = x1 + self.cell_size
                            y2 = y1 + self.cell_size
                            draw.rectangle([x1, y1, x2, y2], fill=color)
                
                image.save(filepath)

                art_info = {"filepath": filepath, "price": price}
                self.vending_machine_items.append(art_info)
                
                messagebox.showinfo("등록 완료", f"'{filename}'으로 저장되었습니다.\n가격: {price}원")
                
                # 갤러리 업데이트
                self.update_gallery()

            except Exception as e:
                messagebox.showerror("오류", f"이미지 저장 중 오류가 발생했습니다:\n{e}")

    def update_gallery(self):
        """자판기 갤러리를 최신 상태로 업데이트합니다."""
        # 기존 갤러리 내용 모두 삭제
        for widget in self.scrollable_gallery_frame.winfo_children():
            widget.destroy()
        
        self.gallery_images.clear() # 이미지 리스트 초기화

        # vending_machine_items에 있는 각 아이템을 갤러리에 추가
        for item in self.vending_machine_items:
            # 각 아이템을 담을 프레임
            item_frame = tk.Frame(self.scrollable_gallery_frame, bd=1, relief="solid")
            item_frame.pack(pady=5, padx=10, fill="x")

            # 이미지 로드 및 리사이즈
            img = Image.open(item["filepath"])
            img.thumbnail((100, 100)) # 썸네일 크기 조절
            photo_img = ImageTk.PhotoImage(img)
            self.gallery_images.append(photo_img) # 가비지 컬렉션 방지

            # 위젯 생성
            img_label = tk.Label(item_frame, image=photo_img)
            img_label.pack(side="left", padx=5, pady=5)

            info_frame = tk.Frame(item_frame)
            info_frame.pack(side="left", padx=10)

            price_label = tk.Label(info_frame, text=f"가격: {item['price']}원", font=("Arial", 12))
            price_label.pack(anchor="w")

            buy_button = tk.Button(info_frame, text="구입")
            buy_button.pack(anchor="w", pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtVendingMachine(root)
    root.mainloop()