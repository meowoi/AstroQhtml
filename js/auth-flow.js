/* ============================================================
   AstroQ — Màn Cấp Thẻ ID & Chọn Nhân Vật
   Roster nhân vật (ảnh 3D: /3d, avatar: /ava), chọn → đổi avatar thẻ ID,
   điền tên → "BẮT ĐẦU HÀNH TRÌNH" → lưu localStorage → dashboard.html
   ============================================================ */
(function () {
  "use strict";
  var LS_USER = "astroq-user", LS_AST = "astroq-asteroids";   // ngôn ngữ: AstroQ.getLang/setLang

  /* Nhân vật — dữ liệu ở js/characters.js (CHỖ DUY NHẤT khai báo), vì
     profile.html cũng cho đổi trang phục từ cùng danh sách này. */
  var CHARACTERS = AstroQChars.all();

  var I18N = {
    vi:{
      a_lang:"Ngôn ngữ", title:"CẤP THẺ ID PHI HÀNH GIA", subtitle:"Chọn nhân vật & đặt tên để bắt đầu", pilot:"PHI HÀNH GIA",
         name_label:"TÊN PHI HÀNH GIA", name_ph:"Nhập tên của bạn…", start:"BẮT ĐẦU HÀNH TRÌNH",
         choose:"CHỌN NHÂN VẬT", role:"CHỨC VỤ", trait:"TÍNH CÁCH", s_pow:"NĂNG LƯỢNG", s_spd:"TỐC ĐỘ", s_iq:"TRÍ TUỆ",
         err_name:"Hãy nhập tên phi hành gia!", clearance:"QUYỀN: TÂN BINH", tap:"Chạm vào một nhân vật để xem thông tin",
         mystery_toast:"Nhân vật bí ẩn — sắp mở khoá!" },
    en:{
      a_lang:"Language", title:"ASTRONAUT ID ISSUE", subtitle:"Pick a character & name to begin", pilot:"PILOT",
         name_label:"PILOT NAME", name_ph:"Enter your name…", start:"START THE JOURNEY",
         choose:"CHOOSE YOUR CHARACTER", role:"ROLE", trait:"PERSONALITY", s_pow:"POWER", s_spd:"SPEED", s_iq:"INTELLECT",
         err_name:"Please enter a pilot name!", clearance:"CLEARANCE: ROOKIE", tap:"Tap a character to view its stats",
         mystery_toast:"Mystery character — unlocking soon!" }
  };
  var LANG = AstroQ.getLang();
  function t(k){ return (I18N[LANG]||I18N.vi)[k] || k; }

  var getUser = AstroQ.getUser;
  var selected = null;

  function applyLang(lang){
    if(lang==="en"||lang==="vi") LANG=lang;
    document.documentElement.lang = LANG;
    document.title = "AstroQ — " + t("title");
    AstroQ.applyTexts(t);
    var np=$("pilot-name"); if(np) np.placeholder = t("name_ph");
    document.querySelectorAll(".lang-switch button").forEach(function(b){ b.classList.toggle("active", b.getAttribute("data-lang")===LANG); });
    if(selected) fillHud(selected);
  }

  function renderRoster(){
    var box=$("roster"); if(!box) return; box.innerHTML="";
    CHARACTERS.forEach(function(c,i){
      var b=document.createElement("button"); b.type="button"; b.className="char"; b.dataset.id=c.id;
      b.style.setProperty("--d",(i*0.15)+"s");
      b.innerHTML='<span class="char-glow"></span><img src="'+c.model+'" alt="'+c.name+'" /><span class="char-nm">'+c.name+'</span>';
      b.addEventListener("click", function(){ select(c.id); });
      box.appendChild(b);
    });
    // Thẻ nhân vật bí ẩn (khoá) — bóng đen + dấu "?" phát sáng
    for(var k=0;k<AstroQChars.MYSTERY;k++){
      var mb=document.createElement("button"); mb.type="button"; mb.className="char mystery"; mb.setAttribute("aria-label","???");
      mb.style.setProperty("--d",((CHARACTERS.length+k)*0.15)+"s");
      mb.innerHTML='<span class="char-glow"></span><span class="silhouette"><span class="q">?</span></span><span class="char-nm">???</span>';
      mb.addEventListener("click", function(){ toast(t("mystery_toast")); });
      box.appendChild(mb);
    }
  }

  function setBar(id,v){ var el=$(id); if(el) el.style.width=Math.max(4,Math.min(100,v))+"%"; }
  function fillHud(c){
    if($("hud-model")) $("hud-model").src=c.model;
    if($("hud-name")) $("hud-name").textContent=c.name;
    if($("hud-role")) $("hud-role").textContent=c.role[LANG]||c.role.vi;
    if($("hud-trait")) $("hud-trait").textContent=c.trait[LANG]||c.trait.vi;
    setBar("stat-pow",c.stats.pow); setBar("stat-spd",c.stats.spd); setBar("stat-iq",c.stats.iq);
  }

  function select(id){
    var c=null; for(var i=0;i<CHARACTERS.length;i++){ if(CHARACTERS[i].id===id){ c=CHARACTERS[i]; break; } }
    if(!c) return;
    selected=c;
    document.querySelectorAll(".char").forEach(function(b){ b.classList.toggle("active", b.dataset.id===id); });
    var av=$("card-ava");
    if(av){ av.style.setProperty("--z", c.zoom||1); av.src=c.ava; av.classList.remove("pop"); void av.offsetWidth; av.classList.add("pop"); }  // thẻ ID đổi avatar + zoom riêng
    if($("hud-info")) $("hud-info").classList.add("show");
    fillHud(c);
  }

  var toast = AstroQ.makeToast("sel-toast", 2200);

  /* ---- BẮT ĐẦU HÀNH TRÌNH ---- */
  function startJourney(){
    var name=($("pilot-name").value||"").trim();
    if(!name){ $("pilot-name").focus(); toast(t("err_name")); return; }
    if(!selected) selected=CHARACTERS[0];
    var existing=getUser()||{};
    // Lưu hồ sơ phi hành gia (kèm alias theo yêu cầu: pilotName / selectedCharacter / purpleAsteroids)
    // Object.assign để GIỮ LẠI uid/email do Firebase ghi lúc đăng ký —
    // ghi đè nguyên object như trước sẽ làm mất uid, hồ sơ không còn gắn với tài khoản.
    var profile = Object.assign({}, existing, {
      name:name, pilotName:name,
      character:selected.id, selectedCharacter:selected.id,
      avatar:selected.ava, avatarZoom:selected.zoom||1,
      email: existing.email||"", purpleAsteroids: existing.purpleAsteroids||0
    });
    try{ localStorage.setItem(LS_USER, JSON.stringify(profile)); }catch(e){}
    // Chỉ khởi tạo số dư cho pilot MỚI. Người cũ đổi nhân vật không bị mất Thiên thạch tím.
    try{ if(localStorage.getItem(LS_AST)===null) localStorage.setItem(LS_AST, "0"); }catch(e){}

    var stamp=$("stamp"); if(stamp) stamp.classList.add("show");   // đóng dấu APPROVED
    var btn=$("start-journey"); if(btn) btn.disabled=true;
    setTimeout(function(){ window.location.href="dashboard.html"; }, 1150);
  }

  function init(){
    renderRoster();
    var u=getUser();
    if(u && (u.pilotName||u.name)) $("pilot-name").value = u.pilotName||u.name;
    select((u && u.character) || CHARACTERS[0].id);   // mặc định chọn nhân vật đầu / đã chọn trước đó
    applyLang(LANG);
    var sb=$("start-journey"); if(sb) sb.addEventListener("click", startJourney);
    var ni=$("pilot-name"); if(ni) ni.addEventListener("keydown", function(e){ if(e.key==="Enter") startJourney(); });
    AstroQ.initLang(applyLang);
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
