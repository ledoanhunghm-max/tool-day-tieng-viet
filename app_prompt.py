import streamlit as st
import json
from google import genai
from PIL import Image

# --- 1. GIAO DIỆN CẤU HÌNH API KEY TỪ NGƯỜI DÙNG ---
with st.sidebar:
    st.header("🔑 Cấu hình hệ thống")
    API_KEY = st.text_input("Nhập Gemini API Key của bạn để sử dụng:", type="password")
    st.markdown("👉 [Nhấn vào đây để tạo API Key miễn phí](https://aistudio.google.com/app/apikey)")
    st.markdown("---")
    st.write("Lưu ý: API Key của bạn chỉ được lưu tạm thời trên trình duyệt và tự xóa khi đóng tab. Ứng dụng không lưu trữ dữ liệu này.")

client = None
if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        st.sidebar.error("API Key không hợp lệ hoặc lỗi kết nối!")

# --- 2. HÀM TẠO KỊCH BẢN ---
def tao_bo_prompt_chuyen_gia(chu_de, danh_sach_anh=None):
    huan_luyen_ai = f"""
    Dữ liệu đầu vào: "{chu_de}"
    
    Mục đích: Chuyên gia dạy tiếng Việt cho người nước ngoài và video marketing.
    Quy tắc:
    1) 10 lượt thoại, chia đều 5 cảnh. Lồng ghép 5 từ vựng, 1-2 ngữ pháp.
    2) Nếu có hội thoại sẵn: Giữ nguyên văn 100%. Nếu chỉ có chủ đề: Tự sáng tác.
    3) Gom toàn bộ lời thoại theo TỪNG NHÂN VẬT ở đầu file.
    """

    if danh_sach_anh and len(danh_sach_anh) > 0:
        huan_luyen_ai += f"""
    [QUY TẮC ĐA NHÂN VẬT]: Có {len(danh_sach_anh)} ảnh. Phân tích CHI TIẾT ngoại hình, TRANG PHỤC của TỪNG NGƯỜI bằng TIẾNG VIỆT. Khớp vai trò logic và duy trì trang phục nhất quán 100%.
    """

    huan_luyen_ai += """
    [QUY TẮC BỐI CẢNH XUYÊN SUỐT - CỰC KỲ QUAN TRỌNG]:
    Để video logic, TẤT CẢ 5 cảnh quay phải diễn ra trong CÙNG MỘT KHÔNG GIAN.
    Bạn phải sáng tạo ra MỘT "master_background" (Bối cảnh gốc) cực kỳ chi tiết bằng TIẾNG VIỆT (Ví dụ: Một quầy bán trái cây bằng gỗ trong khu chợ truyền thống, ngập tràn ánh nắng sáng sớm, có nhiều sạp cam và dưa hấu xung quanh...).
    
    [QUY TẮC NGÔN NGỮ & BẢO VỆ MEDIA]:
    TUYỆT ĐỐI KHÔNG DÙNG TIẾNG ANH. Viết Tiếng Việt 100%.
    
    Bạn PHẢI trả về ĐỘC QUYỀN định dạng JSON sau (không dùng markdown):
    {
        "lesson_goals": "Mục tiêu bài học",
        "target_vocabulary": ["từ 1", "từ 2"],
        "target_grammar": ["Cấu trúc"],
        "master_background": "MÔ TẢ BỐI CẢNH GỐC BẰNG TIẾNG VIỆT CỰC KỲ CHI TIẾT DÙNG CHUNG CHO CẢ VIDEO",
        "character_profiles": "Hồ sơ BẰNG TIẾNG VIỆT CỰC KỲ CHI TIẾT CỦA TẤT CẢ NHÂN VẬT",
        "voiceovers_by_character": [
            {"character_name": "Tên", "lines": ["'Câu 1.'", "'Câu 2.'"]}
        ],
        "scenes": [
            {
                "scene_number": 1,
                "image_prompt": "[PASTE NGUYÊN VĂN character_profiles VÀO ĐÂY]. [TUYỆT ĐỐI KHÔNG CÓ CHỮ HAY SỐ TRONG ẢNH]. Phong cách hoạt hình 3D Pixar, chi tiết sắc nét. BỐI CẢNH: [PASTE NGUYÊN VĂN master_background VÀO ĐÂY]. [Chỉ mô tả thêm Hành động của nhân vật và Góc máy (ví dụ: Quay cận cảnh khuôn mặt) cho cảnh này].",
                "video_prompt": "[PASTE NGUYÊN VĂN character_profiles VÀO ĐÂY]. [TUYỆT ĐỐI KHÔNG CÓ CHỮ HAY SỐ TRONG VIDEO]. Phong cách hoạt hình 3D Pixar hiện đại, chuyển động mượt mà. BỐI CẢNH: [PASTE NGUYÊN VĂN master_background VÀO ĐÂY]. Nhân vật đang mấp máy môi khớp câu thoại: '[TRÍCH DẪN THOẠI]'. [Chỉ mô tả thêm Hành động cụ thể của cảnh này]."
            }
        ]
    }
    """
    
    noi_dung_gui_ai = []
    if danh_sach_anh and len(danh_sach_anh) > 0:
        for anh in danh_sach_anh:
            noi_dung_gui_ai.append(Image.open(anh))
    noi_dung_gui_ai.append(huan_luyen_ai)

    response = client.models.generate_content(model='gemini-2.5-flash', contents=noi_dung_gui_ai)
    return json.loads(response.text.strip().removeprefix("```json").removesuffix("```").strip())

# --- 3. HÀM XUẤT TEXT ---
def xuat_ra_text_rut_gon(du_lieu_json, chu_de):
    noi_dung_txt = f"CHỦ ĐỀ: \n{chu_de}\n" + "="*70 + "\n\n"
    
    # Hiển thị bối cảnh gốc lên đầu để người dùng biết
    noi_dung_txt += "📍 BỐI CẢNH XUYÊN SUỐT CỦA VIDEO:\n"
    noi_dung_txt += f"{du_lieu_json.get('master_background', 'Không có')}\n"
    noi_dung_txt += "="*70 + "\n\n"

    noi_dung_txt += "🎙️ KỊCH BẢN LỒNG TIẾNG:\n" + "-"*50 + "\n"
    for vo in du_lieu_json.get('voiceovers_by_character', []):
        noi_dung_txt += f"👤 NHÂN VẬT: {vo['character_name'].upper()}\n"
        for line in vo.get('lines', []):
            noi_dung_txt += f"{line}\n"
        noi_dung_txt += "\n"
    noi_dung_txt += "="*70 + "\n\n"
    
    for canh in du_lieu_json.get('scenes', []):
        noi_dung_txt += f"🎬 CẢNH {canh['scene_number']}\n🖼️ IMAGE PROMPT:\n{canh['image_prompt']}\n\n🎥 VIDEO PROMPT:\n{canh['video_prompt']}\n" + "-"*70 + "\n\n"
    return noi_dung_txt

# --- 4. GIAO DIỆN WEB ---
st.set_page_config(page_title="App Sinh Prompt Dạy Tiếng Việt", page_icon="🎓", layout="centered")
st.title("🎓 Trạm Sinh Prompt Video Dạy Tiếng Việt")
st.markdown("Hỗ trợ: **Đa nhân vật**, **Bối cảnh xuyên suốt**, **KHÔNG TEXT trong media**, **Tiếng Việt 100%**.")

danh_sach_anh = st.file_uploader("🖼️ BƯỚC 1: Tải ảnh tham chiếu (Có thể chọn nhiều)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
if danh_sach_anh:
    cols = st.columns(len(danh_sach_anh))
    for i, anh in enumerate(danh_sach_anh):
        with cols[i]: st.image(anh, caption=f"Nhân vật {i+1}", width="stretch")

chu_de_input = st.text_area("📥 BƯỚC 2: Nhập chủ đề HOẶC dán hội thoại có sẵn:", height=120)

if st.button("🚀 Xử Lý & Sinh Bộ Prompt", type="primary", width="stretch"):
    if not client:
        st.error("⚠️ Vui lòng mở thanh Sidebar bên trái và nhập API Key của bạn để sử dụng!")
    else:
        with st.spinner("⏳ AI đang xây dựng bối cảnh gốc và xử lý kịch bản..."):
            try:
                ket_qua = tao_bo_prompt_chuyen_gia(chu_de_input, danh_sach_anh)
                ket_qua_txt = xuat_ra_text_rut_gon(ket_qua, chu_de_input)
                st.success("✅ Thành công! Bối cảnh đã được đồng nhất.")
                st.text_area("Xem trước:", ket_qua_txt, height=600)
                st.download_button("💾 Tải File", ket_qua_txt, "Bo_Prompt.txt")
            except Exception as e:
                st.error(f"❌ Lỗi: {e}")
