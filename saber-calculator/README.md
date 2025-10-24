# 🔋 Saber PPA Calculator Suite

**Professional Solar Power Purchase Agreement (PPA) Financial Modeling Platform**

## 🌍 **Live Demo - Try It Now!**

- **MVP Calculator**: https://ppa.saberrenewable.energy
- **Advanced Calculator**: https://ppa-advanced.saberrenewable.energy

*No installation required - accessible worldwide with SSL security*

---

## 🚀 **Quick Start**

### Instant Access
Just click the demo links above! Both calculators are live and ready to use.

### Local Development
```bash
# Clone and run everything in one command
cd saber-calculator
./start_saber_with_tunnels.sh
```

See [QUICK_START.md](QUICK_START.md) for detailed setup instructions.

---

## 📊 **Applications**

### 1. MVP Calculator (`app.py`)
- **URL**: https://ppa.saberrenewable.energy
- **Port**: 8501
- **Purpose**: Basic PPA financial modeling
- **Features**: 10-year projections, debt structuring, IRR calculations

### 2. Advanced Calculator (`calc-proto-cl.py`)
- **URL**: https://ppa-advanced.saberrenewable.energy  
- **Port**: 8502
- **Purpose**: Professional-grade PPA modeling
- **Features**: Full Saber branding, advanced modeling, export capabilities

---

## 🏗️ **Architecture**

- **Frontend**: Streamlit applications
- **Infrastructure**: Cloudflare Tunnels with SSL termination
- **Deployment**: Background services with process management
- **Monitoring**: Log files and port monitoring
- **Domains**: Custom Saber renewable energy domains

---

## 📋 **Documentation**

- [Quick Start Guide](QUICK_START.md) - Complete setup and usage
- [Project Status](PROJECT_STATUS.md) - Technical details and deployment status  
- [Demo Ready](DEMO_READY.md) - Executive summary and demo instructions

---

## 🔧 **Development**

### Tech Stack
- Python 3.12+ with Streamlit
- pandas, numpy, numpy-financial for calculations
- plotly, altair for visualizations
- Cloudflare tunnels for public access

### Service Management
```bash
# Start all services
./start_saber_with_tunnels.sh

# Stop all services  
pkill -f 'streamlit|cloudflared'

# Check status
ps aux | grep -E 'streamlit|cloudflared'
```

---

**🎉 Production Ready | ✅ SSL Secured | 🌍 Globally Accessible**