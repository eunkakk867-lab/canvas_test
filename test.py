import tkinter as tk

class PixelArtVendingMachine:
    def __init__(self, root):
        self.root = root
        self.root.title("픽셀 아트 판매 자판기")
        self.root.geometry("1000x700") # 창의 초기 크기 설정

        # --- 메인 프레임 생성 ---
        # 메인 창을 좌우로 나누기 위한 기본 프레임들을 생성합니다.
        self.create_layout()

    def create_layout(self):
        # 1. 왼쪽 프레임 (픽셀 아트 캔버스 영역)
        # relief="sunken"과 borderwidth=2를 사용하여 시각적으로 구분되도록 합니다.
        canvas_frame = tk.Frame(self.root, bd=2, relief="sunken", padx=10, pady=10)
        # pack을 사용하여 왼쪽에 배치하고, 창 크기 변경 시 함께 늘어나도록 설정 (fill="both", expand=True)
        canvas_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # 프레임의 역할을 알려주는 레이블 추가
        canvas_label = tk.Label(canvas_frame, text="<< 픽셀 아트를 그릴 격자 캔버스 >>", font=("Arial", 14))
        canvas_label.pack(pady=20)

        # 2. 오른쪽 프레임 (자판기 갤러리 영역)
        gallery_frame = tk.Frame(self.root, bd=2, relief="sunken", padx=10, pady=10)
        # pack을 사용하여 오른쪽에 배치하고, 창 크기 변경 시 함께 늘어나도록 설정
        gallery_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # 프레임의 역할을 알려주는 레이블 추가
        gallery_label = tk.Label(gallery_frame, text="<< 자판기 갤러리 >>", font=("Arial", 14))
        gallery_label.pack(pady=20)


if __name__ == "__main__":
    # Tkinter 루트 창 생성
    root = tk.Tk()
    # PixelArtVendingMachine 클래스의 인스턴스 생성
    app = PixelArtVendingMachine(root)
    # GUI 프로그램 실행
    root.mainloop()