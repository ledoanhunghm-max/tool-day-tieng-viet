import streamlit as st
import json
from google import genai
from PIL import Image

# --- 1. CẤU HÌNH API KEY (DÙNG NỘI BỘ) ---
# DÁN API KEY THẬT CỦA BẠN VÀO GIỮA 2 DẤU NGOẶC KÉP BÊN DƯỚI
API_KEY = "AIzaSyCRmfjHRV44ykxwPvLdtuaPqUJFBBMnqqk"
client = genai.Client(api_key=API_KEY)

# --- 2. HÀM TẠO KỊCH BẢN ---
def tao_bo_prompt_chuyen_gia(chu_de, danh_sach_anh=None):
    
    huan_luyen_ai = f"""
    Dữ liệu đầu vào từ người dùng: "{chu_de}"
    
    Hãy thực hiện nhiệm vụ sau:

    --- BẮT ĐẦU NỘI DUNG GEM CỦA BẠN ---
    Mục đích và Mục tiêu:
    * Đóng vai là một chuyên gia về dạy tiếng Việt cho người nước ngoài và chuyên gia video marketing.
    * Tạo ra các kịch bản có cấu trúc rõ ràng, tập trung vào học từ vựng và ngữ pháp.

    Hành vi và Quy tắc:
    1) Phân tích tài liệu và xác định chủ đề chính.
    2) Cấu trúc kịch bản:
    a) Lồng ghép khéo léo ít nhất 5 từ vựng mới.
    b) Áp dụng 1-2 cấu trúc ngữ pháp.
    3) Tư vấn Video Marketing (Góc máy, bối cảnh...).
    4) Quy trình: Phác thảo -> Viết kịch bản -> Đề xuất marketing.

    Phong cách và Tông giọng:
    * Chuyên nghiệp, tận tâm.
    * Ngôn ngữ miền Bắc rõ ràng, truyền cảm hứng (Dùng "quả", "nhé", "ạ"...).
    --- KẾT THÚC NỘI DUNG GEM CỦA BẠN ---
    
    ========================================================
    YÊU CẦU ĐỊNH DẠNG BẮT BUỘC DÀNH CHO HỆ THỐNG APP:
    
    [QUY TẮC XỬ LÝ LỜI THOẠI]:
    1. TRƯỜNG HỢP CÓ SẴN HỘI THOẠI: Giữ nguyên văn 100%. Tuyệt đối không thêm bớt.
    2. TRƯỜNG HỢP CHỈ LÀ CHỦ ĐỀ: Tự sáng tác hội thoại 10 lượt lời.
    CHIA ĐỀU HỘI THOẠI VÀO ĐÚNG 5 CẢNH (Mỗi cảnh 2 câu).
    
    [QUY TẮC VOICEOVER]: 
    Gom toàn bộ lời thoại, chia theo TỪNG NHÂN VẬT ở đầu file. Mỗi câu bọc trong dấu nháy đơn.
    """

    if danh_sach_anh and len(danh_sach_anh) > 0:
        so_luong_anh = len(danh_sach_anh)
        huan_luyen_ai += f"""
    [QUY TẮC PHÂN TÍCH ẢNH THAM CHIẾU ĐA NHÂN VẬT]:
    Tôi có đính kèm {so_luong_anh} bức ảnh. Mỗi bức ảnh đại diện cho một nhân vật.
    Bạn PHẢI "nhìn" TẤT CẢ các bức ảnh này và phân tích CỰC KỲ CHI TIẾT ngoại hình (khuôn mặt, kiểu tóc) và TRANG PHỤC (màu sắc, họa tiết áo/quần) của TỪNG NGƯỜI bằng TIẾNG VIỆT.
    1. Hãy map (khớp) hình ảnh với vai trò nhân vật logic.
    2. Gộp tất cả các phân tích này vào trường "character_profiles".
    3. Duy trì mô tả trang phục của TỪNG NGƯỜI nhất quán 100% xuyên suốt.
    """

    huan_luyen_ai += """
    [QUY TẮC NGÔN NGỮ PROMPT - CỰC KỲ QUAN TRỌNG]:
    TUYỆT ĐỐI KHÔNG SỬ DỤNG TIẾNG ANH trong các trường "character_profiles", "image_prompt" và "video_prompt". TOÀN BỘ mô tả nhân vật, bối cảnh, hành động BẮT BUỘC PHẢI ĐƯỢC VIẾT BẰNG TIẾNG VIỆT 100%.
    
    Bạn PHẢI trả về KẾT QUẢ ĐỘC QUYỀN dưới định dạng JSON sau (không dùng markdown):
    {
        "lesson_goals": "Mục tiêu bài học",
        "target_vocabulary": ["từ 1", "từ 2"],
        "target_grammar": ["Cấu trúc"],
        "character_profiles": "Hồ sơ BẰNG TIẾNG VIỆT CỰC KỲ CHI TIẾT CỦA TẤT CẢ NHÂN VẬT",
        "voiceovers_by_character": [
            {
                "character_name": "Tên",
                "lines": ["'Câu thoại 1.'", "'Câu thoại 2.'"]
            }
        ],
        "scenes": [
            {
                "scene_number": 1,
                "image_prompt": "[PASTE TOÀN BỘ character_profiles TIẾNG VIỆT VÀO ĐÂY]. [TUYỆT ĐỐI KHÔNG để bất kỳ chữ hay số nào xuất hiện TRONG ảnh]. Phong cách hoạt hình 3D Pixar/Disney, chi tiết sắc nét, ánh sáng ấm áp. [Mô tả bối cảnh bằng tiếng Việt].",
                "video_prompt": "[PASTE TOÀN BỘ character_profiles TIẾNG VIỆT VÀO ĐÂY]. [TUYỆT ĐỐI KHÔNG để chữ hay số hiển thị trên video]. Phong cách hoạt hình 3D Pixar/Disney hiện đại, chuyển động mượt mà. Nhân vật đang mấp máy môi và có biểu cảm khớp với câu thoại: '[BẮT BUỘC TRÍCH DẪN LỜI THOẠI CỦA CẢNH NÀY VÀO ĐÂY ĐỂ TẠO KHẨU HÌNH MIỆNG]'. [Mô tả hành động của các nhân vật bằng tiếng Việt]."
            }
        ]
    }
    """

    noi_dung_gui_ai = []
    if danh_sach_anh and len(danh_sach_anh) > 0:
        for anh in danh_sach_anh:
            img = Image.open(anh)
            noi_dung_gui_ai.append(img)
            
    noi_dung_gui_ai.append(huan_luyen_ai)

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=noi_dung_gui_ai
    )
    json_string = response.text.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(json_string)

# --- 3. HÀM XUẤT FILE TEXT RÚT GỌN ---
def xuat_ra_text_rut_gon(du_lieu_json, chu_de):
    noi_dung_txt = f"DỮ LIỆU ĐẦU VÀO: \n{chu_de}\n"
    noi_dung_txt += "="*70 + "\n\n"
    
    noi_dung_txt += "🎙️ KỊCH BẢN LỒNG TIẾNG (VOICEOVER CHUẨN BỊ CHO AI VOICE):\n"
    noi_dung_txt += "-"*50 + "\n"
    
    for vo in du_lieu_json.get('voiceovers_by_character', []):
        noi_dung_txt += f"👤 NHÂN VẬT: {vo['character_name'].upper()}\n"
        for line in vo.get('lines', []):
            noi_dung_txt += f"{line}\n"
        noi_dung_txt += "\n"
    
    noi_dung_txt += "="*70 + "\n\n"
    
    for canh in du_lieu_json.get('scenes', []):
        noi_dung_txt += f"🎬 CẢNH {canh['scene_number']}\n"
        noi_dung_txt += f"🖼️ IMAGE PROMPT:\n{canh['image_prompt']}\n\n"
        noi_dung_txt += f"🎥 VIDEO PROMPT:\n{canh['video_prompt']}\n"
        noi_dung_txt += "-"*70 + "\n\n"
        
    return noi_dung_txt

# --- 4. GIAO DIỆN WEB ---
st.set_page_config(page_title="App Sinh Prompt Dạy Tiếng Việt", page_icon="🎓", layout="centered")

st.title("🎓 Trạm Sinh Prompt Video Dạy Tiếng Việt (Phiên Bản Nội Bộ)")
st.markdown("Hỗ trợ: **Phân tích ĐA NHÂN VẬT**, **Tuyệt đối KHÔNG có TEXT trong media**, và **Prompt THUẦN TIẾNG VIỆT 100%**.")

danh_sach_anh = st.file_uploader("🖼️ BƯỚC 1: Tải lên các ảnh nhân vật tham chiếu (Có thể chọn nhiều ảnh)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if danh_sach_anh:
    st.write(f"Đã tải lên {len(danh_sach_anh)} ảnh nhân vật:")
    cols = st.columns(len(danh_sach_anh))
    for i, anh in enumerate(danh_sach_anh):
        with cols[i]:
            st.image(anh, caption=f"Nhân vật {i+1}", width="stretch")

chu_de_input = st.text_area(
    "📥 BƯỚC 2: Nhập chủ đề HOẶC dán đoạn hội thoại có sẵn của bạn vào đây:", 
    "Một người mẹ và cậu con trai Việt kiều đi chợ mua trái cây để học tên các loại quả bằng tiếng Việt.", 
    height=120
)

if st.button("🚀 Xử Lý & Sinh Bộ Prompt", type="primary", width="stretch"):
    if API_KEY == "DÁN_API_KEY_CỦA_BẠN_VÀO_ĐÂY":
        st.error("⚠️ Chủ app chưa điền API Key ở dòng số 8 trong mã code!")
    else:
        with st.spinner("⏳ AI đang xử lý và thiết kế kịch bản..."):
            try:
                ket_qua_json = tao_bo_prompt_chuyen_gia(chu_de_input, danh_sach_anh)
                noi_dung_file_txt = xuat_ra_text_rut_gon(ket_qua_json, chu_de_input)
                
                st.success("✅ Đã xử lý xong! Mời bạn xem kết quả bên dưới.")
                
                st.text_area("Xem trước Kết quả:", noi_dung_file_txt, height=600)
                
                st.download_button(
                    label="💾 Tải File Prompts (.txt) về máy",
                    data=noi_dung_file_txt,
                    file_name="Bo_Prompt_Noi_Bo.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"❌ Có lỗi xảy ra: {e}")