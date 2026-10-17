# Security Policy

## Overview

AlphaFlow is a production algorithmic trading platform that handles sensitive financial data and API credentials. Security is our top priority. This document outlines our security practices and how to report vulnerabilities.

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 7.0.x   | :white_check_mark: |
| < 7.0   | :x:                |

## Critical Security Rules

### 🔐 API Keys & Credentials

**NEVER commit sensitive credentials to git:**

```bash
# ❌ NEVER commit these files:
.env                    # Contains API keys
*_credentials.json      # Credential files
api_keys.txt           # API key lists
```

**✅ Always use .env for credentials:**

1. Copy `.env.example` to `.env`
2. Add your credentials to `.env`
3. Verify `.env` is in `.gitignore`
4. **NEVER** commit `.env` to version control

### 🛡️ Trading Security

**Paper Trading First:**
- Always test in paper mode before live trading
- Set `ALPACA_PAPER=true` in `.env` for paper trading
- Verify trading mode indicator shows "PAPER MODE" in UI

**Live Trading Precautions:**
- Start with small capital ($1k-$5k maximum)
- Set strict risk limits (2% daily loss)
- Enable email/Slack notifications
- Monitor trades 3x daily minimum
- Test emergency stop button before going live

**API Key Security:**
- Use Alpaca paper keys for testing
- Use Alpaca live keys ONLY for live trading
- Rotate keys if potentially compromised
- Never share keys in issues, pull requests, or discussions

### 🚨 Risk Management

**Mandatory Safety Features:**
- Daily loss limits (default: 2% maximum)
- Position size limits (default: 10% maximum per position)
- Portfolio heat tracking (default: 25% maximum at risk)
- Stop-loss automation (2x ATR below entry)
- Emergency kill switch (stops all trading instantly)

**Configuration Security:**
```bash
# Conservative defaults in .env
MAX_DAILY_LOSS=0.02          # Halt at 2% daily loss
MAX_POSITION_SIZE=0.10       # Max 10% per position
MAX_PORTFOLIO_HEAT=0.25      # Max 25% total at risk
```

## Reporting a Vulnerability

### How to Report

If you discover a security vulnerability, please report it responsibly:

**DO:**
- Email: [Insert security contact email]
- Include detailed description of the vulnerability
- Provide steps to reproduce (if applicable)
- Suggest a fix (if you have one)
- Allow 48 hours for initial response

**DON'T:**
- Create public GitHub issues for security vulnerabilities
- Disclose vulnerabilities publicly before they're fixed
- Exploit vulnerabilities for personal gain
- Share vulnerabilities with third parties

### What to Report

We consider the following as security vulnerabilities:

**Critical:**
- API key exposure or leakage
- Unauthorized trade execution
- Bypass of risk management controls
- Authentication/authorization flaws
- Remote code execution
- SQL injection or similar attacks

**High:**
- Cross-site scripting (XSS)
- Cross-site request forgery (CSRF)
- Sensitive data exposure
- Improper access controls
- Insecure dependencies

**Medium:**
- Information disclosure
- Denial of service (DoS)
- Configuration vulnerabilities

### Response Timeline

- **Initial Response**: Within 48 hours
- **Severity Assessment**: Within 1 week
- **Fix Development**: 1-4 weeks (depending on severity)
- **Security Patch Release**: As soon as fix is tested
- **Public Disclosure**: After fix is released (coordinated with reporter)

### Recognition

We appreciate security researchers who responsibly disclose vulnerabilities:

- Credit in CHANGELOG.md and release notes
- Recognition in project README
- Our sincere gratitude!

## Security Best Practices

### For Developers

**Code Security:**
```python
# ✅ DO: Use environment variables
api_key = os.getenv('ALPACA_API_KEY')

# ❌ DON'T: Hardcode credentials
api_key = "AKIAX7Y9Z..."  # NEVER DO THIS
```

**Input Validation:**
```python
# ✅ DO: Validate all inputs
if position_size > max_position_size:
    raise ValueError("Position size exceeds limit")

# ❌ DON'T: Trust user input
execute_trade(user_input)  # Unsafe!
```

**Dependency Security:**
```bash
# Regularly update dependencies
pip install --upgrade -r requirements.txt

# Check for vulnerabilities
pip-audit  # or safety check
```

### For Users

**System Security:**
- Keep your operating system updated
- Use strong passwords for Alpaca account
- Enable 2FA on Alpaca account
- Use firewall on your machine
- Run on trusted networks only

**Monitoring:**
- Enable email notifications for all trades
- Review trade history daily
- Monitor system health endpoint
- Check Alpaca dashboard regularly
- Set up Slack alerts for critical events

**Data Protection:**
- Encrypt your hard drive
- Use secure .env file permissions: `chmod 600 .env`
- Don't share screenshots with API keys visible
- Clear browser cache on shared computers

## Known Security Considerations

### Current Limitations

1. **No Built-in User Authentication**
   - Current version: Single-user deployment
   - Future: Multi-user support with authentication

2. **Local-Only Deployment**
   - Designed for localhost deployment
   - Not hardened for public internet exposure
   - Use firewall if exposing to network

3. **API Rate Limiting**
   - Alpaca has rate limits (200 requests/minute)
   - Platform respects limits but doesn't enforce them
   - Monitor usage to avoid account restrictions

### Deployment Recommendations

**Development:**
```bash
# Run on localhost only
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

**Production (Local Network):**
```bash
# Use firewall rules to restrict access
# Add authentication layer (future feature)
# Use HTTPS with valid certificates
```

## Security Checklist

### Before Live Trading

- [ ] `.env` file is not in git (`git ls-files | grep .env` shows nothing)
- [ ] Using Alpaca paper keys for testing
- [ ] Email notifications configured and tested
- [ ] Emergency stop button tested
- [ ] Daily loss limits configured correctly
- [ ] Trading mode indicator shows correct mode
- [ ] Firewall configured (if exposing to network)
- [ ] Strong Alpaca account password
- [ ] 2FA enabled on Alpaca account

### Regular Security Maintenance

- [ ] Review trade history weekly
- [ ] Update dependencies monthly: `pip install --upgrade -r requirements.txt`
- [ ] Check for security advisories: https://github.com/advisories
- [ ] Rotate API keys if compromised
- [ ] Review risk parameters quarterly
- [ ] Audit system health logs

## Incident Response

If you suspect a security incident:

1. **Immediately**:
   - Click emergency stop button
   - Stop all running strategies
   - Revoke compromised API keys at Alpaca

2. **Within 1 Hour**:
   - Review trade history for unauthorized trades
   - Check system logs for suspicious activity
   - Change passwords if compromised

3. **Within 24 Hours**:
   - Generate new API keys
   - Update `.env` with new keys
   - Review and fix security vulnerability
   - Document incident for future prevention

4. **Report**:
   - Contact Alpaca if unauthorized trades occurred
   - Report vulnerability to project maintainers
   - File police report if financial crime occurred

## Compliance

### Financial Regulations

Users are responsible for compliance with:
- Securities and Exchange Commission (SEC) regulations
- Financial Industry Regulatory Authority (FINRA) rules
- Local securities laws and regulations
- Tax reporting requirements

### Data Privacy

This platform:
- Does NOT collect user data
- Does NOT transmit data to third parties (except Alpaca API)
- Stores trade history locally only
- Does NOT require personal information

## Contact

**Security Issues**: [Insert security contact email]

**General Questions**: GitHub Discussions or Issues

---

**Last Updated**: January 20, 2026
**Version**: 1.0

**Remember**: Security is everyone's responsibility. When in doubt, ask!
