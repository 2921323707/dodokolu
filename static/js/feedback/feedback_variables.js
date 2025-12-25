// 反馈页面变量和元素引用

// 存储第一步的反馈内容
let feedbackContent = '';

// DOM元素引用
const elements = {
    step1: null,
    step2: null,
    feedbackContentForm: null,
    feedbackContactForm: null,
    backBtn: null,
    submitBtn: null,
    btnText: null,
    btnLoading: null,
    feedbackMessage: null
};

// 初始化元素引用
function initElements() {
    elements.step1 = document.getElementById('step1');
    elements.step2 = document.getElementById('step2');
    elements.feedbackContentForm = document.getElementById('feedbackContentForm');
    elements.feedbackContactForm = document.getElementById('feedbackContactForm');
    elements.backBtn = document.getElementById('backBtn');
    elements.submitBtn = document.getElementById('submitBtn');
    elements.feedbackMessage = document.getElementById('feedbackMessage');

    if (elements.submitBtn) {
        elements.btnText = elements.submitBtn.querySelector('.btn-text');
        elements.btnLoading = elements.submitBtn.querySelector('.btn-loading');
    }
}

