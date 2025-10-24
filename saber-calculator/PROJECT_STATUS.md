# Saber Calculator Project Status
**Last Updated:** September 26, 2025
**Status:** ✅ **FULLY OPERATIONAL WITH CLOUDFLARE TUNNELS**

## Current State
The Saber PPA (Power Purchase Agreement) Calculator is a Streamlit-based web application for solar project financial modeling. **UPDATED:** Both applications are now fully operational and accessible via Cloudflare tunnels with proper domain mapping.

## Project Components

### 1. Main Applications
- **`app.py`**: MVP Solar PPA Calculator
  - Basic 10-year project modeling
  - Debt structuring, IRR calculations
  - Simple tariff and inflation modeling

- **`calc-proto-cl.py`**: Advanced PPA Calculator (MAIN APP)
  - Full Saber branding
  - Sophisticated financial modeling
  - Data export capabilities
  - Professional UI with Plotly charts

### 2. Supporting Files
- **`calc-proto.html`**: Standalone HTML calculator prototype
- **`my_first_agent.py`**: LangChain AI agent for automation
- **`test_pytorch_gpu.py`**: GPU testing utility (uncommitted)
- **`day_of.py`**: Date/time utilities

### 3. Assets
- Complete Saber brand assets (logos, icons)
- Multiple color schemes and formats

## Technical Stack
- **Framework**: Streamlit
- **Data Processing**: pandas, numpy, numpy-financial
- **Visualization**: Plotly, Altair
- **AI/ML**: LangChain (optional)
- **Version Control**: Git (GitHub)

## 🚀 Live Deployment
### Public URLs (via Cloudflare Tunnels):
- **MVP Calculator**: https://ppa.saberrenewable.energy
- **Advanced Calculator**: https://ppa-advanced.saberrenewable.energy

### Local URLs:
- **MVP Calculator**: http://localhost:8501
- **Advanced Calculator**: http://localhost:8502

## Quick Start Guide
```bash
# 1. Navigate to project directory
cd /home/marstack/Projects/saber-calculator/saber-calculator

# 2. Start both applications with tunnels (RECOMMENDED)
./start_saber_with_tunnels.sh

# 3. Or start individually:
./start_mvp_calculator.sh        # MVP on port 8501
./start_advanced_calculator.sh   # Advanced on port 8502

# 4. Start Cloudflare tunnel separately if needed:
cloudflared tunnel run ppa-saber
```

## ⚡ One-Command Setup
```bash
# This starts both apps + tunnel with all public URLs
./start_saber_with_tunnels.sh
```

## Key Features
- Solar PPA financial modeling
- Project cost calculations (EPC, O&M, insurance)
- Debt structuring and service coverage
- IRR and cash flow analysis
- Self-consumption vs export modeling
- Inflation adjustments
- Data export functionality

## ✅ Deployment Complete - Ready for Production

### Infrastructure Status:
- ✅ **Dependencies**: All installed and working
- ✅ **Cloudflare Tunnels**: Active with SSL termination
- ✅ **Domain Mapping**: Custom domains configured
- ✅ **High Availability**: 4 tunnel connections established
- ✅ **Background Services**: All running as daemon processes

### Next Steps for Business Growth:
1. **Scale Usage**: Monitor traffic and performance
2. **Enhanced Features**: Add user accounts, saved scenarios
3. **API Integration**: Connect with CRM/ERP systems
4. **Analytics**: Track usage patterns and user behavior
5. **Multi-tenant**: Support multiple organizations

## Potential Improvements
- Add user authentication
- Database for saving scenarios
- API endpoints for integration
- Enhanced reporting/PDF export
- Multi-project portfolio view
- Sensitivity analysis tools

## Environment Variables
The `.env` file contains API keys for:
- OpenAI (for AI agent features)
- SerpAPI (for search capabilities)

**Note**: These should be rotated if exposed.

## 🔧 Technical Implementation Insights

### Cloudflare Tunnel Configuration
- **Tunnel ID**: `f8d1ccd1-81fe-4299-a180-f615ea08b735`
- **Tunnel Name**: `ppa-saber`
- **Config Location**: `/home/marstack/.cloudflared/config.yml`
- **Ingress Rules**:
  ```yaml
  ingress:
    - hostname: ppa.saberrenewable.energy
      service: http://localhost:8501
    - hostname: ppa-advanced.saberrenewable.energy
      service: http://localhost:8502
  ```

### Service Management
```bash
# Check running services
ps aux | grep streamlit
ss -tulpn | grep 850

# Stop all services
pkill -f 'streamlit|cloudflared'

# Background process management
nohup streamlit run app.py --server.port 8501 --server.headless true > /tmp/mvp_calc.log 2>&1 &
nohup streamlit run calc-proto-cl.py --server.port 8502 --server.headless true > /tmp/advanced_calc.log 2>&1 &
nohup cloudflared tunnel run ppa-saber > /tmp/tunnel.log 2>&1 &
```

### Performance Notes
- **Buffer Size Warning**: Non-critical UDP buffer size optimization available
- **ICMP Proxy**: Disabled due to permissions (doesn't affect HTTP tunneling)
- **Connection Redundancy**: 4 tunnel connections for high availability
- **SSL Termination**: Handled by Cloudflare edge