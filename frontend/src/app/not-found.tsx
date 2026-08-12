import Link from "next/link";
import { TopBar } from "@/components/form-ui";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col bg-white">
      <div className="mx-auto w-full max-w-md px-6 py-6 sm:max-w-lg">
        <TopBar />
        <div className="mt-16 flex flex-col items-center gap-3 text-center">
          <p className="text-sm font-bold text-gray-900">페이지를 찾을 수 없어요</p>
          <p className="text-sm text-gray-500">주소가 잘못됐거나 삭제된 페이지예요.</p>
          <Link
            href="/home"
            className="mt-3 rounded-xl bg-blue-500 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-blue-600 active:scale-[0.99]"
          >
            홈으로 가기
          </Link>
        </div>
      </div>
    </div>
  );
}
