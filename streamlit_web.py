import streamlit as st
import os
from datetime import datetime
import base64
import random
import time

# 页面配置
st.set_page_config(
    page_title="简历通，面试通",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 检查是否存在自定义CSS文件
if os.path.exists("styles.css"):
    local_css("styles.css")

# 应用样式设置
st.markdown("""
<style>
    /* 全局样式 */
    :root {
        --primary-color: #165DFF;
        --secondary-color: #36BFFA;
        --accent-color: #7B61FF;
        --neutral-color: #F5F7FA;
        --dark-color: #1D2129;
        --light-text: #6E7681;
    }
    
    /* 基础样式 */
    body {
        font-family: 'Inter', sans-serif;
        background-color: var(--neutral-color);
    }
    
    /* 标题样式 */
    .main-header {
        font-size: clamp(2rem, 5vw, 3.5rem);
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: fadeIn 0.8s ease-in-out;
    }
    
    .sub-header {
        font-size: clamp(1rem, 2vw, 1.25rem);
        color: var(--light-text);
        margin-bottom: 2rem;
        animation: fadeIn 1s ease-in-out;
    }
    
    .section-header {
        font-size: clamp(1.25rem, 3vw, 1.75rem);
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        color: var(--dark-color);
        position: relative;
        padding-bottom: 0.5rem;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 50px;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        border-radius: 3px;
    }
    
    /* 上传容器 */
    .upload-container {
        border: 2px dashed rgba(22, 93, 255, 0.2);
        border-radius: 1rem;
        padding: 3rem 2rem;
        text-align: center;
        transition: all 0.3s ease;
        background-color: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(5px);
        position: relative;
        overflow: hidden;
    }
    
    .upload-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(22, 93, 255, 0.05), transparent);
        animation: shine 4s infinite linear;
    }
    
    .upload-container:hover {
        border-color: var(--primary-color);
        transform: translateY(-5px);
        box-shadow: 0 10px 25px -5px rgba(22, 93, 255, 0.1), 0 10px 10px -5px rgba(22, 93, 255, 0.04);
    }
    
    /* 结果卡片 */
    .result-card {
        background-color: white;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .result-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    .result-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 3px;
        height: 100%;
        background: linear-gradient(to bottom, var(--primary-color), var(--secondary-color));
    }
    
    /* 按钮样式 */
    .btn-primary {
           background: linear-gradient(135deg, rgba(22, 93, 255, 0.8) 0%, rgba(123, 97, 255, 0.8) 100%);
            color: white;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
            border-radius: 0.5rem;
            padding: 0.75rem 1.5rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            transition: all 0.2s ease;
            border: none;
            box-shadow: 0 4px 6px -1px rgba(22, 93, 255, 0.15);
            display: inline-flex;
            align-items: center;
            justify-content: center;
    }
    
    .btn-primary:hover {
            background: linear-gradient(135deg, rgba(22, 93, 255, 0.9) 0%, rgba(123, 97, 255, 0.9) 100%);
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(22, 93, 255, 0.25);
    }
    
    .btn-primary:active {
        transform: translateY(1px);
    }
    
    .btn-secondary {
        background-color: white;
        color: var(--primary-color);
        border: 1px solid rgba(22, 93, 255, 0.2);
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    
    .btn-secondary:hover {
        background-color: rgba(22, 93, 255, 0.05);
        transform: translateY(-2px);
    }
    
    .btn-secondary:active {
        transform: translateY(1px);
    }
    
    /* 标签页样式 */
    .tab-button {
        background-color: transparent;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        color: var(--light-text);
        position: relative;
    }
    
    .tab-button::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        transition: width 0.3s ease;
    }
    
    .tab-button.active {
        color: var(--dark-color);
    }
    
    .tab-button.active::after {
        width: 100%;
    }
    
    .tab-content {
        display: none;
        padding: 1.5rem 0;
        animation: fadeIn 0.5s ease-in-out;
    }
    
    .tab-content.active {
        display: block;
    }
    
    /* 徽章样式 */
    .badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
        font-weight: 500;
        border-radius: 9999px;
        transition: all 0.2s ease;
    }
    
    .badge:hover {
        transform: translateY(-2px);
    }
    
    .badge-success {
        background-color: rgba(52, 211, 153, 0.1);
        color: #10B981;
    }
    
    .badge-warning {
        background-color: rgba(245, 158, 11, 0.1);
        color: #F59E0B;
    }
    
    .badge-info {
        background-color: rgba(56, 189, 248, 0.1);
        color: #06B6D4;
    }
    
    /* 动画效果 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes shine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* 背景效果 */
    .bg-pattern {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(rgba(22, 93, 255, 0.05) 2px, transparent 2px),
            radial-gradient(rgba(22, 93, 255, 0.05) 2px, transparent 2px);
        background-size: 50px 50px;
        background-position: 0 0, 25px 25px;
        z-index: -1;
    }
    
    /* 侧边栏样式 */
    .css-10oheav {
        background-color: white;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
    }
    
    /* 进度条样式 */
    .progress-bar {
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        position: fixed;
        top: 0;
        left: 0;
        z-index: 100;
        transition: width 0.3s ease;
    }
    
    /* 面试模拟样式 */
    .interview-question {
        background-color: rgba(22, 93, 255, 0.05);
        border-left: 4px solid var(--primary-color);
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0.25rem;
    }
    
    .interview-answer {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 1rem;
        margin-bottom: 1.5rem;
        border-radius: 0.25rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .feedback-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        margin-right: 0.5rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .feedback-positive {
        background-color: rgba(52, 211, 153, 0.1);
        color: #10B981;
    }
    
    .feedback-negative {
        background-color: rgba(239, 68, 68, 0.1);
        color: #EF4444;
    }
    
    .feedback-neutral {
        background-color: rgba(245, 158, 11, 0.1);
        color: #F59E0B;
    }
</style>
""", unsafe_allow_html=True)

# 添加背景图案
st.markdown('<div class="bg-pattern"></div>', unsafe_allow_html=True)

# 添加进度条
st.markdown('<div class="progress-bar" id="progressBar"></div>', unsafe_allow_html=True)

# 页面导航
page = st.sidebar.radio(
    "选择功能",
    ["首页", "简历分析", "面试模拟", "个性化学习资源推荐", "我的报告", "使用指南"],
    format_func=lambda x: f"🏠 {x}" if x == "首页" else f"💼 {x}" if x == "简历分析" else f"🎯 {x}" if x == "面试模拟" else f"📊 {x}" if x == "我的报告" else f"📚 {x}"
)

# 更新会话状态
st.session_state.page = page



# 首页
if page == "首页":
    # 页面标题和介绍
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h1 class='main-header'>简历通，面试通</h1>", unsafe_allow_html=True)
        st.markdown("<p class='sub-header'>利用先进AI技术优化您的简历，提高面试通过率</p>", unsafe_allow_html=True)
    with col2:
        st.image("https://picsum.photos/seed/resumehero/400/400", width=200)
    
    # 功能卡片
    col1, col2 = st.columns(2)


    with col1:
        st.markdown("""
        <div class="result-card" style="height: 280px;">
            <div class="flex items-center mb-3">
                <div class="bg-blue-100 p-3 rounded-lg mr-4">
                    <i class="fa fa-file-text-o text-2xl text-primary-color"></i>
                </div>
                <h3 class="text-xl font-semibold">简历分析</h3>
            </div>
            <p class="text-gray-600 mb-4">上传您的简历或岗位JD，获取AI深度分析和定制化优化建议，让您的简历脱颖而出。</p>
            <a href="?page=resume" class="btn-primary w-full" id="resume-button">立即开始</a>
        </div>
        """, unsafe_allow_html=True)

    
    with col2:
        st.markdown("""
        <div class="result-card" style="height: 280px;">
            <div class="flex items-center mb-3">
                <div class="bg-green-100 p-3 rounded-lg mr-4">
                    <i class="fa fa-comments-o text-2xl text-green-600"></i>
                </div>
                <h3 class="text-xl font-semibold">面试模拟</h3>
            </div>
            <p class="text-gray-600 mb-4">根据不同岗位特性，模拟真实面试场景，获取专业点评，提升面试表现。</p>
            <a href="?page=interview" class="btn-primary w-full">立即开始</a>
        </div>
        """, unsafe_allow_html=True)
    
    # 数据统计
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="result-card text-center p-4">
            <h4 class="text-3xl font-bold text-primary-color">96%</h4>
            <p class="text-gray-600">用户满意度</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="result-card text-center p-4">
            <h4 class="text-3xl font-bold text-primary-color">78%</h4>
            <p class="text-gray-600">面试通过率提升</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="result-card text-center p-4">
            <h4 class="text-3xl font-bold text-primary-color">10k+</h4>
            <p class="text-gray-600">专业面试问题库</p>
        </div>
        """, unsafe_allow_html=True)


# 简历分析页面
elif page == "简历分析":
    st.markdown("### 📄 简历分析")
    
    # 侧边栏 - 用户信息和设置
    with st.sidebar:
        st.markdown("<h3 style='color: var(--primary-color); font-weight: 700;'>分析设置</h3>", unsafe_allow_html=True)
        
        analysis_type = st.radio(
            "分析类型",
            ["简历分析", "岗位JD分析", "简历与JD匹配度分析"]
        )
        
        if analysis_type != "岗位JD分析":
            user_name = st.text_input("您的姓名", "")
            job_title = st.text_input("目标职位", "")
        
        industry = st.selectbox("目标行业", ["技术", "金融", "教育", "医疗", "市场营销", "其他"])
        experience_level = st.select_slider(
            "工作经验",
            options=["应届毕业生", "1-3年", "4-6年", "7-10年", "10年以上"]
        )
        
        st.markdown("---")
        st.markdown("<h3 style='color: var(--primary-color); font-weight: 700;'>分析维度</h3>", unsafe_allow_html=True)
        analysis_dimensions = st.multiselect(
            "选择分析维度",
            ["内容完整性", "关键词匹配", "STAR法则应用", "量化成果", "格式规范", "职业发展路径"],
            default=["内容完整性", "关键词匹配", "STAR法则应用"]
        )
        
        st.markdown("---")
        st.button("💾 保存设置", key="save_settings")
    
    # 主内容区
    st.markdown("### 📤 上传您的简历或岗位JD")
    
    if analysis_type in ["简历分析", "简历与JD匹配度分析"]:
        resume_file = st.file_uploader(
            "拖放或点击上传简历文件 (支持 PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            key="resume_upload"
        )
    
    if analysis_type in ["岗位JD分析", "简历与JD匹配度分析"]:
        jd_file = st.file_uploader(
            "拖放或点击上传岗位JD文件 (支持 PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            key="jd_upload"
        )
    
    # 输入框备选方案
    st.markdown("或者直接粘贴文本内容：")
    text_content = st.text_area("输入文本内容", height=200, key="text_input")
    
    # 分析按钮
    if st.button("🚀 开始分析", key="analyze_button"):
        with st.spinner("AI正在深度分析您的内容..."):
            # 更新进度条
            st.markdown("""
            <script>
                function updateProgress(progress) {
                    document.getElementById('progressBar').style.width = progress + '%';
                }
                
                let progress = 0;
                const interval = setInterval(() => {
                    progress += Math.random() * 5;
                    if (progress > 90) {
                        clearInterval(interval);
                        progress = 90;
                    }
                    updateProgress(progress);
                }, 200);
            </script>
            """, unsafe_allow_html=True)
            
            # 模拟处理时间
            time.sleep(5)
            
            # 更新进度条到100%
            st.markdown("""
            <script>
                setTimeout(() => {
                    document.getElementById('progressBar').style.width = '100%';
                }, 500);
            </script>
            """, unsafe_allow_html=True)
            
            # 模拟生成结果
            if analysis_type == "简历分析":
                analysis_results = {
                    "strengths": ["工作经验丰富", "技能匹配度高", "项目成果显著", "教育背景优秀"],
                    "improvements": ["缺乏量化成果", "技能描述不够具体", "职业目标不明确", "简历格式不够专业"],
                    "suggestions": [
                        "在工作经历中添加具体数据和成果，例如增加了多少销售额、提高了多少效率等",
                        "突出与目标职位相关的核心技能，使用行业术语和流行技术词汇",
                        "明确职业目标和发展方向，让招聘者快速了解您的定位",
                        "使用专业的简历模板，确保格式清晰易读，重点突出"
                    ],
                    "keywords_missing": ["Python", "机器学习", "数据分析", "领导力", "团队管理"],
                    "star_analysis": [
                        {"section": "工作经历1", "score": 75, "feedback": "场景和任务描述清晰，但结果部分缺乏具体数据支撑。"},
                        {"section": "项目经验", "score": 60, "feedback": "任务和行动描述较模糊，建议使用STAR法则重构描述。"}
                    ],
                    "completeness_score": 80,
                    "keyword_score": 65,
                    "star_score": 68,
                    "format_score": 72,
                    "overall_score": 73
                }
            elif analysis_type == "岗位JD分析":
                analysis_results = {
                    "key_requirements": ["3年以上相关工作经验", "熟练掌握Python和机器学习", "良好的沟通和团队协作能力", "项目管理经验"],
                    "preferred_skills": ["数据分析", "深度学习", "自然语言处理", "领导力"],
                    "salary_range": "15k-25k",
                    "career_development": "提供晋升机会和专业培训",
                    "keywords": ["Python", "机器学习", "数据分析", "团队协作", "项目管理"]
                }
            else:  # 简历与JD匹配度分析
                analysis_results = {
                    "match_score": 68,
                    "strengths": ["工作经验与岗位要求匹配", "部分核心技能符合要求"],
                    "improvements": ["缺乏岗位明确要求的数据分析技能", "项目管理经验不足", "简历中未突出领导力"],
                    "suggestions": [
                        "在简历中突出与数据分析相关的项目经验和技能",
                        "补充与项目管理相关的职责和成果",
                        "增加能够体现领导力的具体事例"
                    ],
                    "keyword_match": {
                        "matched": ["Python", "团队协作"],
                        "missing": ["机器学习", "数据分析", "项目管理"]
                    }
                }
            
            # 保存结果到会话状态
            st.session_state.analysis_results = analysis_results
            st.session_state.analysis_type = analysis_type
        
        # 显示分析结果
        st.success("分析完成！")
        st.markdown("### 📊 分析结果")
        
        # 显示得分卡片
        if analysis_type == "简历分析":
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"""
                <div class="result-card text-center p-3">
                    <h4 class="text-xl font-bold text-primary-color">{analysis_results["overall_score"]}分</h4>
                    <p class="text-sm text-gray-600">综合评分</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="result-card text-center p-3">
                    <h4 class="text-xl font-bold text-primary-color">{analysis_results["completeness_score"]}分</h4>
                    <p class="text-sm text-gray-600">内容完整度</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="result-card text-center p-3">
                    <h4 class="text-xl font-bold text-primary-color">{analysis_results["keyword_score"]}分</h4>
                    <p class="text-sm text-gray-600">关键词匹配</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="result-card text-center p-3">
                    <h4 class="text-xl font-bold text-primary-color">{analysis_results["star_score"]}分</h4>
                    <p class="text-sm text-gray-600">STAR法则</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"""
                <div class="result-card text-center p-3">
                    <h4 class="text-xl font-bold text-primary-color">{analysis_results["format_score"]}分</h4>
                    <p class="text-sm text-gray-600">格式规范</p>
                </div>
                """, unsafe_allow_html=True)
        
        elif analysis_type == "简历与JD匹配度分析":
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="result-card text-center p-3">
                    <h4 class="text-2xl font-bold text-primary-color">{analysis_results["match_score"]}分</h4>
                    <p class="text-sm text-gray-600">简历与JD匹配度</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="result-card text-center p-3">
                    <div class="w-full bg-gray-200 rounded-full h-4 mb-2">
                        <div class="bg-primary-color h-4 rounded-full" style="width: 68%"></div>
                    </div>
                    <p class="text-sm text-gray-600">匹配度分布</p>
                </div>
                """, unsafe_allow_html=True)
        
        # 创建标签页
        if analysis_type == "简历分析":
            tabs = ["优势", "改进建议", "STAR法则分析", "关键词分析", "优化建议"]
        elif analysis_type == "岗位JD分析":
            tabs = ["关键要求", "优先技能", "薪资福利", "职业发展", "关键词"]
        else:  # 匹配度分析
            tabs = ["匹配概述", "优势", "改进建议", "关键词匹配", "优化建议"]
        
        active_tab = st.radio("选择查看", tabs, key="tabs_analysis", horizontal=True)
        
        # 优势
        if active_tab == "优势" and analysis_type in ["简历分析", "简历与JD匹配度分析"]:
            st.markdown("#### 您的简历优势")
            for i, strength in enumerate(analysis_results["strengths"]):
                st.markdown(f"""
                <div class="result-card" style="animation-delay: {i*0.1}s">
                    <div class="flex items-start">
                        <div class="bg-green-100 rounded-full p-2 mr-3">
                            <i class="fa fa-check text-green-500"></i>
                        </div>
                        <div>
                            <h4 class="font-semibold text-gray-800">{strength}</h4>
                            <p class="text-gray-600 mt-1">这是您简历的突出亮点，能够吸引招聘者的注意力。</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # 改进建议
        elif active_tab == "改进建议" and analysis_type in ["简历分析", "简历与JD匹配度分析"]:
            st.markdown("#### 需要改进的地方")
            for i, improvement in enumerate(analysis_results["improvements"]):
                st.markdown(f"""
                <div class="result-card" style="animation-delay: {i*0.1}s">
                    <div class="flex items-start">
                        <div class="bg-yellow-100 rounded-full p-2 mr-3">
                            <i class="fa fa-exclamation-triangle text-yellow-500"></i>
                        </div>
                        <div>
                            <h4 class="font-semibold text-gray-800">{improvement}</h4>
                            <p class="text-gray-600 mt-1">这部分内容有提升空间，可以进一步优化以提高简历质量。</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # STAR法则分析
        elif active_tab == "STAR法则分析" and analysis_type == "简历分析":
            st.markdown("#### STAR法则应用分析")
            for analysis in analysis_results["star_analysis"]:
                st.markdown(f"""
                <div class="result-card">
                    <div class="flex justify-between items-center mb-2">
                        <h4 class="font-semibold text-gray-800">{analysis["section"]}</h4>
                        <span class="px-3 py-1 rounded-full text-sm {
                            'bg-green-100 text-green-700' if analysis["score"] > 75 else 
                            'bg-yellow-100 text-yellow-700' if analysis["score"] > 50 else 
                            'bg-red-100 text-red-700'
                        }">{analysis["score"]}分</span>
                    </div>
                    <p class="text-gray-600">{analysis["feedback"]}</p>
                    <div class="mt-3">
                        <h5 class="font-medium text-gray-700 mb-1">STAR法则建议</h5>
                        <ul class="list-disc ml-5 text-gray-600">
                            <li>明确描述情境(Situation)：详细说明您所处的环境和面临的挑战</li>
                            <li>清晰定义任务(Task)：说明您的职责和目标</li>
                            <li>详细描述行动(Action)：说明您采取的具体行动和方法</li>
                            <li>量化成果(Result)：用具体数据和指标说明您的成果和贡献</li>
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # 关键词分析
        elif active_tab == "关键词分析" and analysis_type == "简历分析":
            st.markdown("#### 关键词分析")
            st.markdown("**目标行业高频关键词**")
            
            # 显示关键词标签
            present_keywords = ["Python", "领导力", "沟通能力", "团队合作", "数据分析"]
            for keyword in present_keywords:
                st.markdown(f'<span class="badge badge-success">{keyword}</span>', unsafe_allow_html=True)
            
            st.markdown("**建议添加的关键词**")
            for keyword in analysis_results["keywords_missing"]:
                st.markdown(f'<span class="badge badge-warning">{keyword}</span>', unsafe_allow_html=True)
            
            # 添加关键词密度图表
            st.markdown("#### 关键词密度分析")
            st.image("https://picsum.photos/seed/keywordchart/600/300", caption="关键词密度分布图")
        
        # 关键要求 (JD分析)
        elif active_tab == "关键要求" and analysis_type == "岗位JD分析":
            st.markdown("#### 岗位关键要求")
            for requirement in analysis_results["key_requirements"]:
                st.markdown(f"""
                <div class="result-card">
                    <div class="flex items-center">
                        <div class="bg-blue-100 rounded-full p-2 mr-3">
                            <i class="fa fa-check-circle text-blue-500"></i>
                        </div>
                        <span class="text-gray-800">{requirement}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # 优先技能 (JD分析)
        elif active_tab == "优先技能" and analysis_type == "岗位JD分析":
            st.markdown("#### 优先考虑的技能")
            for skill in analysis_results["preferred_skills"]:
                st.markdown(f"""
                <div class="result-card">
                    <div class="flex items-center">
                        <div class="bg-purple-100 rounded-full p-2 mr-3">
                            <i class="fa fa-star text-purple-500"></i>
                        </div>
                        <span class="text-gray-800">{skill}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # 匹配概述 (匹配度分析)
        elif active_tab == "匹配概述" and analysis_type == "简历与JD匹配度分析":
            st.markdown("#### 简历与岗位JD匹配概述")
            st.markdown(f"""
            <div class="result-card">
                <p class="text-gray-700 mb-3">您的简历与目标岗位的匹配度为 {analysis_results["match_score"]} 分。这个分数表明您具备一些岗位所需的技能和经验，但仍有提升空间。</p>
                
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-green-50 p-3 rounded-lg">
                        <h5 class="font-medium text-green-700 mb-1">优势领域</h5>
                        <ul class="list-disc ml-5 text-gray-600">
                            {"".join([f"<li>{strength}</li>" for strength in analysis_results["strengths"]])}
                        </ul>
                    </div>
                    
                    <div class="bg-yellow-50 p-3 rounded-lg">
                        <h5 class="font-medium text-yellow-700 mb-1">改进领域</h5>
                        <ul class="list-disc ml-5 text-gray-600">
                            {"".join([f"<li>{improvement}</li>" for improvement in analysis_results["improvements"]])}
                        </ul>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 关键词匹配 (匹配度分析)
        elif active_tab == "关键词匹配" and analysis_type == "简历与JD匹配度分析":
            st.markdown("#### 关键词匹配情况")
            
            st.markdown("**已匹配的关键词**")
            for keyword in analysis_results["keyword_match"]["matched"]:
                st.markdown(f'<span class="badge badge-success">{keyword}</span>', unsafe_allow_html=True)
            
            st.markdown("**缺失的关键词**")
            for keyword in analysis_results["keyword_match"]["missing"]:
                st.markdown(f'<span class="badge badge-warning">{keyword}</span>', unsafe_allow_html=True)
            
            # 匹配度图表
            st.markdown("#### 技能匹配度")
            st.image("https://picsum.photos/seed/skillmatch/600/300", caption="技能匹配度分析")
        
        # 优化建议
        elif active_tab in ["优化建议", "薪资福利", "职业发展", "关键词"]:
            if analysis_type in ["简历分析", "简历与JD匹配度分析"]:
                st.markdown("#### 详细优化建议")
                for suggestion in analysis_results["suggestions"]:
                    st.markdown(f"""
                    <div class="p-3 bg-blue-50 rounded-lg mb-2 border-l-4 border-blue-500">
                        <i class="fa fa-lightbulb text-blue-500 mr-2"></i>
                        <span class="text-gray-700">{suggestion}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 优化后的简历预览按钮
                st.markdown("#### 优化后的简历预览")
                st.markdown("""
                    <div class="result-card p-5 shadow-lg">
                    <div class="mb-4 pb-4 border-b border-gray-200">
                        <h2 class="text-2xl font-bold text-gray-800">候选人姓名</h2>
                        <p class="text-blue-600 font-medium">高级数据分析师</p>
                        <div class="flex flex-wrap mt-2 text-sm text-gray-600">
                            <div class="mr-4"><i class="fa fa-envelope mr-1"></i> email@example.com</div>
                            <div class="mr-4"><i class="fa fa-phone mr-1"></i> +123 456 7890</div>
                            <div><i class="fa fa-linkedin mr-1"></i> linkedin.com/in/yourprofile</div>
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <h3 class="text-lg font-semibold text-gray-800 mb-2">职业概述</h3>
                        <p class="text-gray-700">拥有5年数据分析经验的专业人士，擅长使用Python和机器学习技术解决复杂业务问题。在金融和电商领域有丰富的项目经验，能够从海量数据中提取有价值的见解，为业务决策提供支持。</p>
                    </div>
                    
                    <div class="mb-4">
                        <h3 class="text-lg font-semibold text-gray-800 mb-2">工作经验</h3>
                        <div class="ml-4 mb-3">
                            <div class="flex justify-between">
                                <h4 class="font-medium text-gray-800">高级数据分析师 - 科技公司</h4>
                                <span class="text-sm text-gray-600">2020 - 至今</span>
                            </div>
                            <ul class="list-disc ml-5 mt-1 text-gray-700">
                                <li>设计并实施用户行为分析系统，通过机器学习算法识别高价值客户，使客户转化率提升35%</li>
                                <li>领导5人数据分析团队，开发商业智能仪表盘，为管理层提供实时数据支持，缩短决策周期40%</li>
                                <li>优化推荐算法，提高个性化推荐准确率28%，带动平台销售额增长15%</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <h3 class="text-lg font-semibold text-gray-800 mb-2">教育背景</h3>
                        <div class="ml-4">
                            <div class="flex justify-between">
                                <h4 class="font-medium text-gray-800">计算机科学硕士 - 顶尖大学</h4>
                                <span class="text-sm text-gray-600">2017 - 2019</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# 面试模拟页面
elif page == "面试模拟":
    st.markdown("### 🎯 面试模拟")
    
    # 侧边栏 - 用户信息和设置
    with st.sidebar:
        st.markdown("<h3 style='color: var(--primary-color); font-weight: 700;'>面试设置</h3>", unsafe_allow_html=True)
        
        job_type = st.selectbox("选择岗位类型", ["技术岗", "管培生", "市场营销岗", "金融岗"])
        question_count = st.slider("问题数量", 1, 10, 5)
        
        st.markdown("---")
        st.button("💾 保存设置", key="save_interview_settings")
    
    # 主内容区
    st.markdown("### 📋 开始面试模拟")
    
    if st.button("🚀 开始模拟", key="start_interview"):
        with st.spinner("正在生成面试问题..."):
            # 模拟调用大模型生成问题
            time.sleep(2)
            
            # 不同岗位的问题示例
            if job_type == "技术岗":
                questions = [
                    "请简要介绍一下您在数据分析项目中使用的机器学习算法。",
                    "如何确保数据的准确性和完整性？",
                    "在处理大规模数据时，您会采取哪些优化策略？",
                    "请分享一次您解决复杂技术问题的经历。",
                    "如何评估一个机器学习模型的性能？"
                ]
            elif job_type == "管培生":
                questions = [
                    "请描述您对管培生项目的理解和期望。",
                    "在团队合作中，您如何发挥自己的优势？",
                    "如果遇到团队成员之间的冲突，您会如何处理？",
                    "请举例说明您的领导能力。",
                    "如何快速适应新的工作环境和任务？"
                ]
            elif job_type == "市场营销岗":
                questions = [
                    "请分享一个您成功策划的市场营销活动案例。",
                    "如何进行市场调研和分析？",
                    "在社交媒体营销方面，您有哪些经验和策略？",
                    "如何提高品牌知名度和美誉度？",
                    "请描述您对数字化营销的理解和应用。"
                ]
            elif job_type == "金融岗":
                questions = [
                    "请解释一下金融风险管理的重要性和方法。",
                    "如何分析和评估投资项目的风险和回报？",
                    "在金融市场波动较大的情况下，您会采取哪些投资策略？",
                    "请分享您对金融科技发展趋势的看法。",
                    "如何与客户建立良好的信任关系？"
                ]
            
            selected_questions = random.sample(questions, question_count)
        
        st.success("问题生成完成！")
        st.markdown("### 📝 面试问题")
        
        for i, question in enumerate(selected_questions):
            st.markdown(f"""
            <div class="interview-question">
                <h4 class="font-semibold text-gray-800">问题 {i + 1}</h4>
                <p class="text-gray-600">{question}</p>
            </div>
            """, unsafe_allow_html=True)
            
            answer = st.text_area(f"回答问题 {i + 1}", key=f"answer_{i}")
            
            if st.button(f"提交回答 {i + 1}", key=f"submit_{i}"):
                with st.spinner("正在评估您的回答..."):
                    # 模拟调用大模型评估回答
                    time.sleep(2)
                    
                    # 模拟评估结果
                    feedback = random.choice(["回答非常出色，逻辑清晰，案例丰富！", "回答有一定的思路，但还可以更加具体和深入。", "回答不太准确，建议重新组织语言。"])
                    feedback_type = random.choice(["positive", "neutral", "negative"])
                    
                st.markdown(f"""
                <div class="interview-answer">
                    <h4 class="font-semibold text-gray-800">您的回答</h4>
                    <p class="text-gray-600">{answer}</p>
                    <h4 class="font-semibold text-gray-800">专业点评</h4>
                    <span class="feedback-badge feedback-{feedback_type}">{feedback}</span>
                </div>
                """, unsafe_allow_html=True)


# 个性化学习资源推荐页面
elif page == "个性化学习资源推荐":
    st.markdown("### 📚 个性化学习资源推荐")
    st.write("根据您的学习偏好和历史数据，为您精心挑选了以下学习资源：")

    # 预留推荐资源展示区域
    st.subheader("推荐学习资源列表")
    # 这里可以调用具体的推荐算法获取资源列表，暂时用占位符代替
    recommended_resources = []  # 假设这里是从后端获取的推荐资源列表
    if recommended_resources:
        for resource in recommended_resources:
            st.markdown(f"- {resource}")
    else:
        st.info("暂时没有为您推荐的学习资源，我们会尽快根据您的情况生成合适的推荐。")

    # 预留个性化设置区域
    st.subheader("个性化设置")
    st.write("您可以在这里调整您的学习偏好，以获得更精准的推荐。")
    # 以下是一些示例设置项，可根据实际需求修改
    interest_topics = st.multiselect(
        "您感兴趣的主题",
        ["编程", "设计", "管理", "营销", "语言学习"]
    )
    learning_level = st.selectbox(
        "学习水平",
        ["初级", "中级", "高级"]
    )
    if st.button("保存设置"):
        # 这里可以调用保存设置的接口，暂时用占位符代替
        st.success("设置已保存，我们将根据新的偏好为您更新推荐。")


# 我的报告页面
elif page == "我的报告":
    st.markdown("### 📊 我的报告")
    st.write("该功能正在开发中，敬请期待！")

# 使用指南页面
elif page == "使用指南":
    st.markdown("### 📚 使用指南")
    st.write("以下是使用本系统的详细步骤：")
    st.markdown("1. **首页**：浏览系统的主要功能和数据统计信息。")
    st.markdown("2. **简历分析**：选择分析类型，上传简历或岗位JD，点击“开始分析”按钮，系统将为您提供详细的分析结果和优化建议。")
    st.markdown("3. **面试模拟**：选择岗位类型和问题数量，点击“开始模拟”按钮，系统将生成面试问题，您可以输入回答并提交，系统将为您提供专业点评。")
    st.markdown("4. **我的报告**：查看您的历史分析报告和面试模拟记录。（该功能正在开发中）")
    st.markdown("5. **使用指南**：查看本使用指南，了解系统的使用方法和注意事项。")