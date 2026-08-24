# RAGAB AI TRADE — Production Foundation

## Stack
- Next.js full-stack application
- PostgreSQL + Prisma
- NextAuth-ready authentication layer
- Market-data adapter
- AI signal adapter
- Broker execution adapter
- Compliance/audit schema

PostgreSQL 18 is the current supported major release as of August 2026. Use a supported minor release in production.

## Run locally
1. Install Node.js 20+.
2. Copy `.env.example` to `.env`.
3. Create a PostgreSQL database and set DATABASE_URL.
4. Run:
   npm install
   npx prisma generate
   npx prisma db push
   npm run dev

## Production
Deploy the Next.js application to a managed host and use managed PostgreSQL. Set environment variables in the host's secret manager.

## Security
Never commit `.env`, passwords, database URLs, broker keys or AI keys.
Use TLS, strong AUTH_SECRET, rate limiting, 2FA, secure cookies, audit logs and least-privilege database credentials.

## Live trading gate
BROKER_LIVE_ENABLED must remain false until:
- appropriate regulatory authorisation exists;
- legal/compliance review is complete;
- authorised broker/execution provider is contracted;
- custody and payment arrangements are approved;
- KYC/AML and client-risk controls are operational.

The broker adapter intentionally refuses live orders while the flag is false.
