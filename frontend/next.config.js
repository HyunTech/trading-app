/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    // ESLint 에러가 있어도 프로덕션 빌드를 진행
    ignoreDuringBuilds: true,
  },
};
module.exports = nextConfig;
