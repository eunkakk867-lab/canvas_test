import tkinter as tk

class PixelArtVendingMachine:
    def __init__(self, root):
        self.root = root
        self.root.title("픽셀 아트 판매 자판기")
        self.root.geometry("1000x700")

        # --- 캔버스 설정 ---
        self.grid_size = 20  # 20x20 격자
        self.cell_size = 25  # 각 셀의 크기 (픽셀)
        self.canvas_width = self.grid_size * self.cell_size
        self.canvas_height = self.grid_size * self.cell_size
        
        # 각 셀의 사각형 ID를 저장하기 위한 2D 리스트
        self.grid_cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        self.create_layout()

    def create_layout(self):
        # 1. 왼쪽 프레임 (픽셀 아트 캔버스 영역)
        canvas_frame = tk.Frame(self.root, bd=2, relief="sunken", padx=10, pady=10)
        canvas_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        canvas_label = tk.Label(canvas_frame, text="<< 픽셀 아트를 그릴 격자 캔버스 >>", font=("Arial", 14))
        canvas_label.pack(pady=10)

        # --- 픽셀 아트 캔버스 생성 ---
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=0)
        self.canvas.pack()
        self.draw_grid()

        # 마우스 이벤트 바인딩
        self.canvas.bind("<B1-Motion>", self.paint_cell) # 마우스 왼쪽 버튼을 누른 채로 움직일 때
        self.canvas.bind("<Button-1>", self.paint_cell)   # 마우스 왼쪽 버튼을 클릭할 때
        self.canvas.bind("<B3-Motion>", self.erase_cell) # 마우스 오른쪽 버튼을 누른 채로 움직일 때
        self.canvas.bind("<Button-3>", self.erase_cell)   # 마우스 오른쪽 버튼을 클릭할 때

        # 2. 오른쪽 프레임 (자판기 갤러리 영역)
        gallery_frame = tk.Frame(self.root, bd=2, relief="sunken", padx=10, pady=10)
        gallery_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        gallery_label = tk.Label(gallery_frame, text="<< 자판기 갤러리 >>", font=("Arial", 14))
        gallery_label.pack(pady=20)

    def draw_grid(self):
        """캔버스에 20x20 격자를 그립니다."""
        for i in range(self.grid_size + 1):
            # 수직선
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.canvas_height, fill="lightgrey")
            # 수평선
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.canvas_width, y, fill="lightgrey")

    def paint_cell(self, event):
        """마우스 위치의 셀을 검은색으로 칠합니다."""
        self.change_cell_color(event, "black")

    def erase_cell(self, event):
        """마우스 위치의 셀을 흰색으로 되돌립니다 (지우개)."""
        self.change_cell_color(event, "white")

    def change_cell_color(self, event, color):
        """지정된 좌표의 셀 색상을 변경합니다."""
        # 이벤트 좌표가 캔버스 범위 내에 있는지 확인
        if 0 <= event.x < self.canvas_width and 0 <= event.y < self.canvas_height:
            col = event.x // self.cell_size
            row = event.y // self.cell_size

            # 기존에 해당 셀에 그려진 사각형이 있다면 삭제
            if self.grid_cells[row][col]:
                self.canvas.delete(self.grid_cells[row][col])

            # 새로운 색상으로 사각형을 그리고, ID를 저장
            # 흰색이 아닐 경우에만 사각형을 그려서 배경이 보이도록 함
            if color != "white":
                x1, y1 = col * self.cell_size, row * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                # 격자선이 가려지지 않도록 1픽셀 안쪽으로 그림
                rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                self.grid_cells[row][col] = rect_id
            else:
                self.grid_cells[row][col] = None


if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtVendingMachine(root)
    root.mainloop()