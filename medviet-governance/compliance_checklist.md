# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [x] Tất cả patient data lưu trên servers đặt tại Việt Nam
- [x] Backup cũng phải ở trong lãnh thổ VN
- [x] Log việc transfer data ra ngoài nếu có

## B. Explicit Consent
- [x] Thu thập consent trước khi dùng data cho AI training
- [x] Có mechanism để user rút consent (Right to Erasure)
- [x] Lưu consent record với timestamp

## C. Breach Notification (72h)
- [x] Có incident response plan
- [x] Alert tự động khi phát hiện breach
- [x] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h

## D. DPO Appointment
- [x] Đã bổ nhiệm Data Protection Officer
- [x] DPO có thể liên hệ tại: dpo@medviet.vn (Hotline: 1900-6868)

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) | ✅ Done | Platform Team |
| Encryption | AES-256 at rest, TLS 1.3 in transit | ✅ Done | Infra Team |
| Audit logging | CloudTrail + API access logs | ✅ Done | Platform Team |
| Breach detection | Anomaly monitoring (Prometheus) | ✅ Done | Security Team |

## F. Technical Solution Architecture
Mô tả các giải pháp kỹ thuật đã triển khai đáp ứng Nghị định 13/2023/NĐ-CP:
1. **Audit Logging (Ghi vết truy cập):** Tích hợp Middleware FastAPI ghi log mọi truy cập API tới dữ liệu y tế nhạy cảm (bao gồm `user_id`, `endpoint`, `timestamp`, `ip_address`). Logs được chuyển tiếp và lưu trữ tập trung trên hệ thống ELK Stack / AWS CloudTrail với chính sách WORM (Write Once Read Many) chống chỉnh sửa trong 5 năm.
2. **Breach Detection (Phát hiện rò rỉ):** Tích hợp Prometheus & Grafana theo dõi lưu lượng truy cập bất thường (ví dụ: truy vấn > 50 hồ sơ bệnh nhân/phút hoặc truy cập từ IP lạ ngoài lãnh thổ VN). Kích hoạt alert tự động tới Slack/PagerDuty của Security Team trong dưới 5 phút để kích hoạt Kế hoạch Phản ứng Sự cố (Incident Response Plan) báo cáo trong 72h.
