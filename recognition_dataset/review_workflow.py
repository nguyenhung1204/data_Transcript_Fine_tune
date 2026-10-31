"""Offline human-review helpers for OCR crop candidates."""

from __future__ import annotations

import json
from urllib.parse import quote

MAX_LABEL_LENGTH = 90


def apply_review_annotations(rows, document):
    """Apply an exported review file without promoting OCR suggestions implicitly."""
    if not isinstance(document, dict) or document.get("version") != 1:
        raise ValueError("Review file must be an object with version=1.")
    annotations = document.get("annotations")
    if not isinstance(annotations, list):
        raise ValueError("Review file annotations must be a list.")

    by_id = {row.get("crop_id"): dict(row) for row in rows}
    if None in by_id or len(by_id) != len(rows):
        raise ValueError("Crop manifest contains missing or duplicate crop IDs.")
    seen = set()
    for annotation in annotations:
        if not isinstance(annotation, dict):
            raise ValueError("Each annotation must be an object.")
        crop_id = annotation.get("crop_id")
        if crop_id in seen:
            raise ValueError(f"Duplicate crop ID in review file: {crop_id}")
        seen.add(crop_id)
        row = by_id.get(crop_id)
        if row is None:
            raise ValueError(f"Unknown crop ID in review file: {crop_id}")
        # Previously confirmed manual labels are immutable through OCR review imports.
        if row.get("label_source") == "user_confirmed_labeler_crop":
            continue
        if row.get("label_source") != "ocr_pseudo_label":
            raise ValueError(f"Crop is not an OCR candidate: {crop_id}")
        status = annotation.get("status")
        if status not in {"verified", "rejected", "needs_review"}:
            raise ValueError(f"Invalid review status for {crop_id}: {status}")
        transcript = annotation.get("transcript", "")
        if not isinstance(transcript, str):
            raise ValueError(f"Transcript must be text for {crop_id}.")
        if status == "verified" and (not transcript.strip() or any(c in transcript for c in "\r\n\t")):
            raise ValueError(f"Verified transcript must be non-empty and one line: {crop_id}")
        if status == "verified" and len(transcript) > MAX_LABEL_LENGTH:
            raise ValueError(f"Verified transcript exceeds the {MAX_LABEL_LENGTH}-character training limit: {crop_id}")
        row["transcript"] = transcript
        row["label_status"] = status
        row["label_source"] = "human_visual_review" if status == "verified" else "ocr_pseudo_label"
        reviewed_at = annotation.get("reviewed_at", "")
        row["notes"] = f"Human review status={status}; reviewed_at={reviewed_at}".strip()
    return list(by_id.values())


def build_review_html(rows):
    items = []
    for row in rows:
        page = int(row["page"])
        items.append({
            "id": row["crop_id"],
            "invoice": row["document_id"],
            "pdf": row["filename"],
            "page": page,
            "split": row["split"],
            "text": row.get("transcript") or row.get("raw_ocr_text", ""),
            "raw_length": len(row.get("raw_ocr_text", "")),
            "confidence": row.get("confidence", ""),
            "status": row.get("label_status", "needs_review"),
            "coords": [row.get("x0"), row.get("y0"), row.get("x1"), row.get("y1")],
            "image": "../" + row["crop_path"].replace("\\", "/"),
            "page_image": f"../rendered_pages/{row['document_id']}/page_{page:03d}.png",
            "pdf_path": "../source_300_invoices/pdfs/" + quote(row["filename"], safe=""),
        })
    payload = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    return _HTML.replace("__DATA__", payload).replace("__MAX_LENGTH__", str(MAX_LABEL_LENGTH))


_HTML = r'''<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rà nhãn crop OCR</title>
<style>
:root{font:15px system-ui;color:#17243a;background:#eef3f9}*{box-sizing:border-box}body{margin:0}header{position:sticky;top:0;z-index:2;background:#fff;padding:10px 16px;border-bottom:1px solid #d7e0ec;box-shadow:0 2px 8px #15274312}h1{font-size:20px;margin:0 0 6px}.toolbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap}input,select,button,textarea{font:inherit;padding:8px 10px;border:1px solid #c7d3e2;border-radius:7px;background:white;color:inherit}button{cursor:pointer;font-weight:600}button.primary{background:#2056ce;color:#fff;border-color:#2056ce}button.danger{color:#a22820}#save{font-size:13px;color:#247c60;margin-left:auto}.hint{font-size:13px;color:#596b84;margin:5px 0 0}.layout{display:grid;grid-template-columns:minmax(300px,42%) 1fr;gap:12px;padding:12px;height:calc(100vh - 120px);min-height:450px}.panel{background:#fff;border:1px solid #d6dfeb;border-radius:10px;overflow:auto;padding:12px}.panel h2{font-size:14px;text-transform:uppercase;color:#64758c;margin:0 0 8px}.crop{width:100%;max-height:34vh;object-fit:contain;background:#e9edf3;border:1px solid #dce3ec}.page{width:100%;height:calc(100% - 32px);object-fit:contain;object-position:top center;background:#e9edf3}.pdf-viewer{width:100%;height:calc(100% - 32px);min-height:65vh;border:0;background:#e9edf3}.meta{font-size:13px;color:#596b84}.panel textarea{width:100%;min-height:96px;resize:vertical;font-family:ui-monospace,monospace;margin:5px 0}.buttons{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}.nav{display:flex;align-items:center;gap:8px}.nav button{min-width:82px}.right-head{display:flex;justify-content:space-between;align-items:center;gap:8px}.empty{padding:20px;color:#65748a}@media(max-width:850px){.layout{height:auto;grid-template-columns:1fr}.panel{min-height:42vh}.page,.pdf-viewer{height:55vh}#save{margin-left:0}}
</style></head><body>
<header><h1>Rà transcript OCR — chỉ xác nhận sau khi so với PDF</h1>
<div class="toolbar"><input id="q" placeholder="Tìm mã hóa đơn hoặc nội dung"><select id="split"><option value="">Mọi tập</option><option value="train">Train</option><option value="val">Validation</option><option value="test">Test</option></select><select id="status"><option value="needs_review">Chưa rà</option><option value="all">Tất cả</option><option value="verified">Đã xác nhận</option><option value="rejected">Loại crop</option></select><select id="confidence"><option value="">Mọi confidence</option><option value="low">Thấp (&lt;80%)</option><option value="medium">Trung bình (80–95%)</option><option value="high">Cao (≥95%)</option></select><select id="length-filter"><option value="">Mọi độ dài</option><option value="within">OCR ≤ __MAX_LENGTH__ ký tự</option><option value="over">OCR &gt; __MAX_LENGTH__ ký tự</option></select><button id="export">Tải tiến độ JSON</button><button id="import">Nạp tiến độ JSON</button><input id="file" type="file" accept="application/json" hidden><span id="save"></span></div>
<p class="hint">Trong PDF gốc, bôi đen chữ rồi nhấn Ctrl+C; quay lại ô transcript và nhấn Ctrl+V. Nếu PDF là ảnh scan nên không chọn được chữ, dùng transcript OCR làm gợi ý và đối chiếu bằng ảnh trang.</p></header>
<main class="layout"><section class="panel"><div class="right-head"><h2>Ảnh crop</h2><span id="position" class="meta"></span></div><div id="cropbox" class="empty">Đang tải crop…</div><p id="metadata" class="meta"></p><label for="transcript"><b>Transcript nhìn thấy chính xác trên PDF</b></label><textarea id="transcript" spellcheck="false"></textarea><p id="length" class="meta"></p><div class="buttons"><button class="primary" id="confirm">Xác nhận đúng</button><button class="danger" id="reject">Loại crop</button><button id="undo">Bỏ đánh giá</button></div><div class="nav"><button id="prev">← Trước</button><button id="next">Tiếp →</button><span id="counts" class="meta"></span></div></section>
<section class="panel"><div class="right-head"><h2 id="viewer-title">PDF gốc · bôi đen để copy</h2><div class="buttons"><button id="show-pdf">PDF gốc · copy chữ</button><button id="show-image">Ảnh trang</button><a id="openpage" target="_blank" rel="noopener">Mở PDF riêng</a></div></div><div id="pagebox" class="empty">Chọn crop để xem hóa đơn.</div></section></main>
<script>
const data=__DATA__, key='paddleocr-recognition-review-v1', $=s=>document.querySelector(s);let state={}, index=0, current=null, viewerMode='pdf';
try{state=JSON.parse(localStorage.getItem(key)||'{}')}catch(e){$('#save').textContent='Không đọc được tiến độ trình duyệt'}
for(const x of data)if(!state[x.id]&&['verified','rejected'].includes(x.status))state[x.id]={status:x.status,transcript:x.text,reviewed_at:''};
function status(x){return state[x.id]?.status||x.status||'needs_review'}
function filtered(){const q=$('#q').value.trim().toLowerCase(),s=$('#split').value,st=$('#status').value,cf=$('#confidence').value,lf=$('#length-filter').value;return data.filter(x=>{const c=Number(x.confidence),has=Number.isFinite(c)&&x.confidence!=='';return(!q||`${x.invoice} ${x.pdf} ${x.text}`.toLowerCase().includes(q))&&(!s||x.split===s)&&(st==='all'||status(x)===st)&&(!cf||(cf==='low'&&has&&c<.8)||(cf==='medium'&&has&&c>=.8&&c<.95)||(cf==='high'&&has&&c>=.95))&&(!lf||(lf==='over'&&x.raw_length>__MAX_LENGTH__)||(lf==='within'&&x.raw_length<=__MAX_LENGTH__))})}
function esc(x){return String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function save(){try{localStorage.setItem(key,JSON.stringify(state));$('#save').textContent='Đã lưu trong trình duyệt'}catch(e){$('#save').textContent='Không lưu được tự động — hãy tải JSON ngay'}}
function draw(){const rows=filtered();if(!rows.length){current=null;$('#position').textContent='0 / 0';$('#cropbox').innerHTML='<p class="empty">Không còn crop khớp bộ lọc.</p>';$('#pagebox').innerHTML='';$('#metadata').textContent='';$('#transcript').value='';$('#length').textContent='';$('#counts').textContent=`${data.length} crop tổng cộng`;return}index=Math.max(0,Math.min(index,rows.length-1));current=rows[index];const a=state[current.id],pdfUrl=`${current.pdf_path}#page=${current.page}&toolbar=1&view=FitH`;$('#position').textContent=`${index+1} / ${rows.length}`;$('#cropbox').innerHTML=`<img class="crop" src="${esc(current.image)}" alt="Crop ${esc(current.id)}">`;$('#pagebox').innerHTML=viewerMode==='pdf'?`<iframe class="pdf-viewer" src="${esc(pdfUrl)}" title="PDF gốc, trang ${current.page}"></iframe>`:`<img class="page" src="${esc(current.page_image)}" alt="Trang ${current.page}">`;$('#viewer-title').textContent=viewerMode==='pdf'?'PDF gốc · bôi đen để copy':'Ảnh trang đã render';$('#openpage').href=viewerMode==='pdf'?pdfUrl:current.page_image;$('#openpage').textContent=viewerMode==='pdf'?'Mở PDF riêng':'Mở ảnh riêng';$('#metadata').textContent=`${current.invoice} · ${current.pdf} · trang ${current.page} · ${current.split} · confidence ${current.confidence} · tọa độ ${current.coords.join(', ')} · trạng thái ${status(current)}`;$('#transcript').value=a?.transcript??current.text??'';updateLength();$('#counts').textContent=`Đã xác nhận ${Object.values(state).filter(v=>v.status==='verified').length} · loại ${Object.values(state).filter(v=>v.status==='rejected').length} · tổng ${data.length}`}
function updateLength(){const n=$('#transcript').value.length,over=n>__MAX_LENGTH__,longSuggestion=current&&current.raw_length>__MAX_LENGTH__;$('#length').textContent=`${n}/__MAX_LENGTH__ ký tự${over?' — vượt giới hạn; không rút gọn nếu crop/PDF có đủ chữ. Hãy để chờ rà hoặc cắt lại vùng chữ.':''}${longSuggestion?' · OCR gợi ý dài quá giới hạn; kiểm tra crop có gom nhiều dòng không.':''}`;$('#length').style.color=over||longSuggestion?'#a22820':'';$('#confirm').disabled=over}
function mark(s){if(!current)return;const transcript=$('#transcript').value;if(s==='verified'&&(!transcript.trim()||/[\r\n\t]/.test(transcript)||transcript.length>__MAX_LENGTH__)){alert('Nhãn xác nhận phải chính xác, nằm trên một dòng và không quá __MAX_LENGTH__ ký tự.');return}state[current.id]={status:s,transcript,reviewed_at:new Date().toISOString()};save();draw()}
$('#confirm').onclick=()=>mark('verified');$('#reject').onclick=()=>mark('rejected');$('#undo').onclick=()=>{if(current){delete state[current.id];save();draw()}};$('#prev').onclick=()=>{index=Math.max(0,index-1);draw()};$('#next').onclick=()=>{index=Math.min(filtered().length-1,index+1);draw()};$('#q').oninput=()=>{index=0;draw()};$('#split').onchange=$('#status').onchange=$('#confidence').onchange=$('#length-filter').onchange=()=>{index=0;draw()};$('#transcript').oninput=updateLength;
$('#show-pdf').onclick=()=>{viewerMode='pdf';draw()};$('#show-image').onclick=()=>{viewerMode='image';draw()};
$('#export').onclick=()=>{const blob=new Blob([JSON.stringify({version:1,annotations:Object.entries(state).map(([crop_id,v])=>({crop_id,...v}))},null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='review_annotations.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};
$('#import').onclick=()=>$('#file').click();$('#file').onchange=async e=>{try{const obj=JSON.parse(await e.target.files[0].text());if(obj.version!==1||!Array.isArray(obj.annotations))throw Error('Định dạng file không hợp lệ');const ids=new Set(data.map(x=>x.id));for(const a of obj.annotations){if(!ids.has(a.crop_id))throw Error(`Không tìm thấy crop ${a.crop_id}`);if(!['verified','rejected','needs_review'].includes(a.status))throw Error('Trạng thái không hợp lệ')}for(const a of obj.annotations)state[a.crop_id]={status:a.status,transcript:a.transcript||'',reviewed_at:a.reviewed_at||''};save();index=0;draw();alert('Đã nạp tiến độ rà soát.')}catch(err){alert(`Không nạp được file: ${err.message}`)}e.target.value=''};
document.addEventListener('keydown',e=>{if(['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName))return;if(e.key==='ArrowRight')$('#next').click();if(e.key==='ArrowLeft')$('#prev').click();if(e.ctrlKey&&e.key==='Enter')$('#confirm').click()});draw();
</script></body></html>'''
