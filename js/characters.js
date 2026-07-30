/* ============================================================
   characters.js — DANH SÁCH NHÂN VẬT, CHỖ DUY NHẤT khai báo.

   Trước 29/07/2026 mảng này nằm riêng trong js/auth-flow.js. Tách ra vì
   `profile.html` (Hồ sơ Phi Hành Gia) cũng cho đổi trang phục, mà copy 10
   dòng dữ liệu sang trang thứ hai là chắc chắn có ngày hai bên lệch nhau.

   Nạp TRƯỚC js/auth-flow.js và trước script riêng của profile.html:
     <script src="js/characters.js"></script>

   API:
     AstroQChars.all()          → mảng nhân vật (bản sao, sửa không ảnh hưởng gốc)
     AstroQChars.byId("m")      → một nhân vật, null nếu không có
     AstroQChars.MYSTERY        → số ô "???" chưa mở khoá
     AstroQChars.avatarOf(u)    → ảnh avatar theo hồ sơ người dùng (có đường lùi)
     AstroQChars.zoomOf(u)      → mức zoom avatar tương ứng

   role/trait/stats vẫn là dữ liệu tạm (giữ nguyên như bản cũ, chờ cập nhật).
   ============================================================ */
(function (global) {
  "use strict";

  var CHARACTERS = [
    { id:"m",     name:"Comet",    model:"3d/m3d.png",     ava:"ava/avam.png",     role:{vi:"Phi công trưởng",en:"Chief Pilot"},   trait:{vi:"Lanh lợi & tò mò",en:"Quick & curious"},  stats:{pow:78,spd:90,iq:74} },
    { id:"b",     name:"Byte",     model:"3d/b3d.png",     ava:"ava/avab.png",     role:{vi:"Kỹ sư hệ thống",en:"Systems Engineer"},trait:{vi:"Điềm tĩnh & logic",en:"Calm & logical"}, stats:{pow:70,spd:66,iq:95} },
    { id:"q",     name:"Quark",    model:"3d/q3d.png",     ava:"ava/q2.png",       role:{vi:"Trinh sát",en:"Scout"},               trait:{vi:"Nhanh nhẹn & tinh nghịch",en:"Nimble & playful"}, stats:{pow:60,spd:96,iq:70} },
    { id:"raica", name:"Castor",   model:"3d/raica3d.png", ava:"ava/avaraica.png", zoom:1.6, role:{vi:"Chỉ huy",en:"Commander"},   trait:{vi:"Quyết đoán & ấm áp",en:"Decisive & warm"}, stats:{pow:88,spd:72,iq:82} },
    { id:"bao",   name:"Umbra",    model:"3d/bao3D.png",   ava:"ava/avabao.png",   role:{vi:"Đội trưởng tấn công",en:"Strike Leader"},trait:{vi:"Dũng mãnh & nhanh",en:"Fierce & fast"}, stats:{pow:94,spd:92,iq:66} },
    { id:"chim",  name:"Ignis",    model:"3d/chim3D.png",  ava:"ava/avachim.png",  role:{vi:"Hoa tiêu",en:"Navigator"},            trait:{vi:"Tự do & tinh mắt",en:"Free & sharp-eyed"}, stats:{pow:64,spd:88,iq:80} },
    { id:"cho",   name:"Sirius",   model:"3d/cho2.png",    ava:"ava/avacho.png",   role:{vi:"Vệ binh",en:"Guardian"},              trait:{vi:"Trung thành & gan dạ",en:"Loyal & brave"}, stats:{pow:82,spd:78,iq:72} },
    { id:"chuot", name:"Lyrae",    model:"3d/chuot3d.png", ava:"ava/avachuot.png", role:{vi:"Thợ máy",en:"Mechanic"},              trait:{vi:"Khéo léo & lanh",en:"Handy & sharp"}, stats:{pow:58,spd:84,iq:86} },
    { id:"cu",    name:"Moros",    model:"3d/cu3d.png",    ava:"ava/avacu.png",    role:{vi:"Nhà thiên văn",en:"Astronomer"},      trait:{vi:"Uyên bác & trầm",en:"Wise & quiet"}, stats:{pow:62,spd:60,iq:98} },
    { id:"cua",   name:"Karkinos", model:"3d/cua3d.png",   ava:"ava/avacua.png",   role:{vi:"Kỹ thuật viên giáp",en:"Armor Tech"}, trait:{vi:"Cứng cỏi & lì",en:"Tough & sturdy"}, stats:{pow:90,spd:54,iq:70} }
  ];

  /** Số ô "???" hiện kèm roster (nhân vật chưa mở khoá). */
  var MYSTERY = 2;

  function byId(id) {
    for (var i = 0; i < CHARACTERS.length; i++) {
      if (CHARACTERS[i].id === id) return CHARACTERS[i];
    }
    return null;
  }

  /* Ảnh avatar theo hồ sơ, có đường lùi: hồ sơ ghi sẵn `avatar` (bản cũ) →
     tra theo `character` → cuối cùng lấy nhân vật đầu danh sách. Nhờ vậy hồ sơ
     lưu từ trước khi có file này vẫn hiện đúng ảnh. */
  function avatarOf(u) {
    if (u && u.avatar) return u.avatar;
    var c = u && byId(u.character || u.selectedCharacter);
    return (c || CHARACTERS[0]).ava;
  }
  function zoomOf(u) {
    if (u && u.avatarZoom) return u.avatarZoom;
    var c = u && byId(u.character || u.selectedCharacter);
    return (c && c.zoom) || 1;
  }

  global.AstroQChars = {
    // Trả bản sao nông: trang nào lỡ sort/đổi mảng thì không làm hỏng trang khác
    all: function () { return CHARACTERS.slice(); },
    byId: byId,
    MYSTERY: MYSTERY,
    avatarOf: avatarOf,
    zoomOf: zoomOf
  };
})(window);
