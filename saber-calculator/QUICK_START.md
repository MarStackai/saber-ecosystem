# 🚀 Saber Calculator Quick Start Guide

## ✨ **Instant Access - No Setup Required**

### 🌍 **Public Demo URLs:**
- **MVP Calculator**: https://ppa.saberrenewable.energy
- **Advanced Calculator**: https://ppa-advanced.saberrenewable.energy

*These are live, production-ready applications accessible from anywhere in the world.*

---

## 🛠️ **Local Development Setup**

### Prerequisites
- Python 3.12+ with virtual environment
- Git repository cloned locally

### One-Command Start
```bash
cd /home/marstack/Projects/saber-calculator/saber-calculator
./start_saber_with_tunnels.sh
```

This single command will:
- ✅ Start MVP Calculator on port 8501
- ✅ Start Advanced Calculator on port 8502  
- ✅ Launch Cloudflare tunnel
- ✅ Display all access URLs

### Individual Component Startup
```bash
# Start MVP Calculator only
./start_mvp_calculator.sh

# Start Advanced Calculator only
./start_advanced_calculator.sh

# Start Cloudflare tunnel only
cloudflared tunnel run ppa-saber
```

---

## 📊 **Application Features**

### MVP Calculator (`app.py`)
- **Purpose**: Basic PPA financial modeling
- **Features**: 
  - 10-year project projections
  - Simple debt structuring
  - Basic tariff modeling
  - IRR calculations
- **Best For**: Quick estimates, initial feasibility

### Advanced Calculator (`calc-proto-cl.py`)
- **Purpose**: Professional-grade PPA modeling
- **Features**:
  - Full Saber branding and styling
  - Advanced financial modeling
  - Comprehensive cash flow analysis
  - Data export capabilities (CSV, JSON)
  - Professional charts and visualizations
- **Best For**: Client presentations, detailed analysis

---

## 🔧 **Service Management**

### Check Status
```bash
# Check running applications
ps aux | grep streamlit

# Check port usage
ss -tulpn | grep 850

# Check tunnel status
ps aux | grep cloudflared
```

### Stop Services
```bash
# Stop all Saber Calculator services
pkill -f 'streamlit|cloudflared'

# Or stop individually
pkill -f "streamlit.*8501"  # MVP Calculator
pkill -f "streamlit.*8502"  # Advanced Calculator
pkill -f "cloudflared"      # Tunnel
```

### Restart Services
```bash
# Quick restart everything
pkill -f 'streamlit|cloudflared' && sleep 2 && ./start_saber_with_tunnels.sh
```

---

## 🌐 **Infrastructure Details**

### Cloudflare Tunnel Configuration
- **Tunnel Name**: `ppa-saber`
- **Tunnel ID**: `f8d1ccd1-81fe-4299-a180-f615ea08b735`
- **SSL**: Automatic SSL termination at Cloudflare edge
- **Redundancy**: 4 connection endpoints for high availability

### Domain Mapping
```yaml
ingress:
  - hostname: ppa.saberrenewable.energy
    service: http://localhost:8501
  - hostname: ppa-advanced.saberrenewable.energy
    service: http://localhost:8502
```

---

## 🎯 **Demo Scenarios**

### For Executive Demos
1. **Start with Advanced Calculator**: https://ppa-advanced.saberrenewable.energy
2. **Input realistic project**: 50kWp commercial solar installation
3. **Show professional output**: Branded reports, financial projections
4. **Demonstrate export**: Download data for further analysis

### For Technical Demos
1. **Show both applications**: Compare MVP vs Advanced features
2. **Demonstrate local development**: Show startup scripts and logs
3. **Explain infrastructure**: Cloudflare tunnels, domain routing
4. **Show monitoring**: Process management, port usage

---

## 📋 **Troubleshooting**

### Common Issues

**Port Already in Use**
```bash
# Find and kill process using port
lsof -ti:8501 | xargs kill
lsof -ti:8502 | xargs kill
```

**Tunnel Connection Issues**
```bash
# Restart tunnel
pkill -f cloudflared
cloudflared tunnel run ppa-saber
```

**Application Won't Start**
```bash
# Check logs
tail -f /tmp/mvp_calc.log
tail -f /tmp/advanced_calc.log
tail -f /tmp/tunnel.log
```

### Log Locations
- MVP Calculator: `/tmp/mvp_calc.log`
- Advanced Calculator: `/tmp/advanced_calc.log`
- Cloudflare Tunnel: `/tmp/tunnel.log`

---

## 🔄 **Environment Setup (First Time)**

If starting from scratch:

```bash
# 1. Navigate to project
cd /home/marstack/Projects/saber-calculator/saber-calculator

# 2. Configure Python environment (done automatically)
# Virtual environment: /home/marstack/Projects/saber-calculator/.venv/

# 3. Dependencies already installed:
# streamlit, pandas, numpy, numpy-financial, plotly, altair, etc.

# 4. Start services
./start_saber_with_tunnels.sh
```

---

## 📈 **Next Steps**

### Immediate Actions
- [ ] Test both applications with real project data
- [ ] Share public URLs with stakeholders
- [ ] Gather user feedback

### Future Enhancements
- [ ] User authentication system
- [ ] Database for saved scenarios
- [ ] API endpoints for integrations
- [ ] Usage analytics and monitoring
- [ ] Multi-tenant support

---

**🎉 Ready to go! Both calculators are live and accessible worldwide.**