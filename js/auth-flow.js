/* ============================================================
   AstroQ — Màn Cấp Thẻ ID & Chọn Nhân Vật
   Roster nhân vật (ảnh 3D: /3d, avatar: /ava), chọn → đổi avatar thẻ ID,
   điền tên → "BẮT ĐẦU HÀNH TRÌNH" → lưu localStorage → dashboard.html
   ============================================================ */
(function () {
  "use strict";
  var LS_USER = "astroq-user", LS_AST = "astroq-asteroids";   // ngôn ngữ: AstroQ.getLang/setLang

  /* Nhân vật — ghép ảnh 3D (thư mục 3d) với avatar (thư mục ava).
     role/trait/stats là dữ liệu tạm (sẽ cập nhật sau). */
  var CHARACTERS = [
    { id:"m",     name:"Comet", model:"3d/m3d.png",     ava:"ava/avam.png",     role:{vi:"Phi công trưởng",en:"Chief Pilot"},   trait:{vi:"Lanh lợi & tò mò",en:"Quick & curious"},  stats:{pow:78,spd:90,iq:74} },
    { id:"b",     name:"Byte",  model:"3d/b3d.png",     ava:"ava/avab.png",     role:{vi:"Kỹ sư hệ thống",en:"Systems Engineer"},trait:{vi:"Điềm tĩnh & logic",en:"Calm & logical"}, stats:{pow:70,spd:66,iq:95} },
    { id:"q",     name:"Quark", model:"3d/q3d.png",     ava:"ava/q2.png",       role:{vi:"Trinh sát",en:"Scout"},               trait:{vi:"Nhanh nhẹn & tinh nghịch",en:"Nimble & playful"}, stats:{pow:60,spd:96,iq:70} },
    { id:"raica", name:"Castor",   model:"3d/raica3d.png", ava:"ava/avaraica.png", zoom:1.6, role:{vi:"Chỉ huy",en:"Commander"},             trait:{vi:"Quyết đoán & ấm áp",en:"Decisive & warm"}, stats:{pow:88,spd:72,iq:82} },
    { id:"bao",   name:"Umbra",    model:"3d/bao3D.png",   ava:"ava/avabao.png",   role:{vi:"Đội trưởng tấn công",en:"Strike Leader"},trait:{vi:"Dũng mãnh & nhanh",en:"Fierce & fast"}, stats:{pow:94,spd:92,iq:66} },
    { id:"chim",  name:"Ignis",    model:"3d/chim3D.png",  ava:"ava/avachim.png",  role:{vi:"Hoa tiêu",en:"Navigator"},            trait:{vi:"Tự do & tinh mắt",en:"Free & sharp-eyed"}, stats:{pow:64,spd:88,iq:80} },
    { id:"cho",   name:"Sirius",   model:"3d/cho2.png",    ava:"ava/avacho.png",   role:{vi:"Vệ binh",en:"Guardian"},              trait:{vi:"Trung thành & gan dạ",en:"Loyal & brave"}, stats:{pow:82,spd:78,iq:72} },
    { id:"chuot", name:"Lyrae",    model:"3d/chuot3d.png", ava:"ava/avachuot.png", role:{vi:"Thợ máy",en:"Mechanic"},              trait:{vi:"Khéo léo & lanh",en:"Handy & sharp"}, stats:{pow:58,spd:84,iq:86} },
    { id:"cu",    name:"Moros",    model:"3d/cu3d.png",    ava:"ava/avacu.png",    role:{vi:"Nhà thiên văn",en:"Astronomer"},      trait:{vi:"Uyên bác & trầm",en:"Wise & quiet"}, stats:{pow:62,spd:60,iq:98} },
    { id:"cua",   name:"Karkinos", model:"3d/cua3d.png",   ava:"ava/avacua.png",   role:{vi:"Kỹ thuật viên giáp",en:"Armor Tech"}, trait:{vi:"Cứng cỏi & lì",en:"Tough & sturdy"}, stats:{pow:90,spd:54,iq:70} }
  ];

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
    // 2 thẻ nhân vật bí ẩn (khoá) — bóng đen + dấu "?" phát sáng
    for(var k=0;k<2;k++){
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
    var profile={
      name:name, pilotName:name,
      character:selected.id, selectedCharacter:selected.id,
      avatar:selected.ava, avatarZoom:selected.zoom||1, email:existing.email||"", purpleAsteroids:0
    };
    try{ localStorage.setItem(LS_USER, JSON.stringify(profile)); }catch(e){}
    try{ localStorage.setItem(LS_AST, "0"); }catch(e){}   // nhiên liệu (Thiên thạch tím) ban đầu = 0

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
