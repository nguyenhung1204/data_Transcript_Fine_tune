from __future__ import annotations
import csv, json, pathlib, collections, hashlib
ROOT = pathlib.Path(__file__).resolve().parent if '__file__' in globals() else pathlib.Path(r'E:\KhoaLuanTotNghiep\data_Transcript_Fine_tune\recognition_dataset')
OUT = ROOT / 'colab_finetune'
PROGRESS = ROOT / 'automatic_review' / 'manual_review_progress.json'
SOURCE = ROOT / 'automatic_review' / 'automatic_review_manifest.csv'
AUDIT = ROOT / 'automatic_review' / 'train_review_audit.csv'

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    annotations = json.loads(PROGRESS.read_text(encoding='utf-8'))['annotations']
    source_rows = {r['crop_id']: r for r in read_csv(SOURCE)}
    audit_rows = read_csv(AUDIT) if AUDIT.exists() else []
    audit_verified = {r['crop_id'] for r in audit_rows if r.get('new_status') == 'verified'}
    split_lines = {s: [] for s in ('train', 'val', 'test')}
    exported=[]; issues=[]; invoice_splits={}; label_counts=collections.Counter(); split_counts=collections.Counter()
    for ann in annotations:
        if ann.get('status') != 'verified': continue
        cid=ann.get('crop_id',''); row=source_rows.get(cid)
        if row is None:
            issues.append((cid,'missing_manifest')); continue
        text=ann.get('transcript',''); split=row.get('split',''); image=row.get('crop_path','')
        if not text.strip(): issues.append((cid,'blank_transcript')); continue
        if any(ch in text for ch in '\t\r\n'): issues.append((cid,'tab_or_newline')); continue
        if len(text)>90: issues.append((cid,'over_90_chars')); continue
        if split not in split_lines: issues.append((cid,'invalid_split')); continue
        image_path=ROOT/image
        if not image_path.is_file(): issues.append((cid,'missing_image')); continue
        inv=row.get('document_id','')
        old=invoice_splits.setdefault(inv,split)
        if old != split: issues.append((cid,'invoice_split_leak')); continue
        if cid in audit_verified or row.get('label_source') == 'user_confirmed_labeler_crop': origin='human_review_evidence'
        elif row.get('label_source') == 'ocr_pseudo_label': origin='automatic_pdf_ocr_confirmation_or_untraced_verified'
        else: origin='verified_status_origin_unclassified'
        split_lines[split].append(f'{image}\t{text}')
        manifest_row={k:row.get(k,'') for k in ('crop_id','document_id','invoice_id','filename','source_pdf_sha256','page','x0','y0','x1','y1','crop_path','split','field_type','confidence','label_source','review_status','review_reasons','ocr1_text','ocr2_text','pdf_text','pdf_text_found','pdf_text_matches_ocr1','pdf_text_line_count','geometry_valid','pdf_sha256_verified','is_machine_consensus')}
        manifest_row.update({'transcript':text,'annotation_status':ann['status'],'annotation_reviewed_at':ann.get('reviewed_at',''),'provenance_class':origin,'transcript_length':len(text)})
        exported.append(manifest_row); split_counts[split]+=1; label_counts[origin]+=1
    if issues: raise SystemExit('Export aborted; validation issues: '+repr(issues[:25])+f' (total {len(issues)})')
    fields=list(exported[0]) if exported else []
    for split,lines in split_lines.items():
        (OUT/f'{split}.txt').write_text(('\n'.join(lines)+'\n') if lines else '',encoding='utf-8')
    with (OUT/'dataset_manifest.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(exported)
    summary={'generated_from':'automatic_review/manual_review_progress.json + automatic_review/automatic_review_manifest.csv','source_progress_sha256':hashlib.sha256(PROGRESS.read_bytes()).hexdigest(),'source_manifest_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'verified_annotations':len(exported),'split_crop_counts':dict(split_counts),'split_invoice_counts':{s:len({x['document_id'] for x in exported if x['split']==s}) for s in split_lines},'provenance_counts':dict(label_counts),'rejected':sum(a.get('status')=='rejected' for a in annotations),'needs_review':sum(a.get('status')=='needs_review' for a in annotations),'max_label_chars':90,'image_files_copied':False,'notes':['The progress status "verified" includes automatic confirmations; it does not mean every label was manually read by a person.','Only rows with a matching audit record or original labeler confirmation are marked human_review_evidence.','OCR/PDF consensus is weak supervision and not equivalent to visual ground truth.','The current progress record does not contain an independent OCR2 confirmation for the automatically confirmed labels.','Split is inherited from invoice-level manifest; same invoice is kept in one split.']}
    (OUT/'dataset_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
