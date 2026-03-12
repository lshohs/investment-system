export default function MyDayPinkPlanner() {
  const React = window.React;
  const { useMemo, useState } = React;

  const [selectedDate] = useState("2026-03-11");
  const [todayFocus, setTodayFocus] = useState("오늘은 나를 너무 몰아붙이지 않고, 해야 할 일과 쉬는 시간을 함께 챙기기");
  const [mustDo, setMustDo] = useState([
    "블로그 글감 1개 정리하기",
    "가벼운 산책 30분",
    "책 20쪽 읽기",
  ]);
  const [routineChecks, setRoutineChecks] = useState({
    morning: true,
    reading: false,
    walk: false,
    coffee: true,
    writing: false,
  });

  const weeklyRoutine = useMemo(
    () => [
      { day: "월", items: ["블로그 정리", "독서", "가계부"] },
      { day: "화", items: ["산책", "논산 기록", "휴식"] },
      { day: "수", items: ["커피 기록", "블로그 작성", "정리"] },
      { day: "목", items: ["독서", "일정 점검", "산책"] },
      { day: "금", items: ["글쓰기", "카페 메모", "휴식"] },
      { day: "토", items: ["가벼운 외출", "사진 정리", "자유 시간"] },
      { day: "일", items: ["주간 돌아보기", "다음 주 준비", "느긋한 시간"] },
    ],
    []
  );

  const toggle = (key) => {
    setRoutineChecks((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const StatCard = ({ label, value, note }) => (
    <div className="rounded-[28px] bg-white/85 backdrop-blur border border-white shadow-sm p-5">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-bold text-slate-800">{value}</div>
      {note ? <div className="mt-2 text-sm text-slate-500">{note}</div> : null}
    </div>
  );

  const SectionCard = ({ title, subtitle, children }) => (
    <section className="rounded-[32px] bg-white/90 backdrop-blur border border-white shadow-sm p-6 md:p-7">
      <div className="mb-4">
        <h2 className="text-xl md:text-2xl font-bold text-slate-800">{title}</h2>
        {subtitle ? <p className="mt-1 text-sm text-slate-500">{subtitle}</p> : null}
      </div>
      {children}
    </section>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-100 via-pink-50 to-fuchsia-100 text-slate-800 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        <div className="rounded-[36px] bg-gradient-to-r from-pink-300 via-rose-300 to-fuchsia-300 p-7 md:p-9 shadow-sm mb-6 text-white">
          <div className="text-sm md:text-base opacity-90">하루를 차분하게 정리하는 생활 플래너</div>
          <div className="mt-2 text-3xl md:text-4xl font-bold tracking-tight">나의 하루</div>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3 max-w-4xl">
            <div className="rounded-2xl bg-white/20 px-4 py-3 backdrop-blur">오늘 날짜 · {selectedDate}</div>
            <div className="rounded-2xl bg-white/20 px-4 py-3 backdrop-blur">기분 · 잔잔하고 밝게</div>
            <div className="rounded-2xl bg-white/20 px-4 py-3 backdrop-blur">오늘의 목표 · 무리하지 않기</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <StatCard label="오늘 꼭 할 일" value="3개" note="너무 많지 않게, 꼭 필요한 것만" />
          <StatCard label="루틴 체크" value="2 / 5" note="조금씩 채워가는 하루" />
          <StatCard label="이번 주 흐름" value="차분함" note="조절하면서 가는 리듬" />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[1.05fr_0.95fr] gap-6">
          <div className="space-y-6">
            <SectionCard title="오늘의 하루" subtitle="하루의 중심을 먼저 정리합니다.">
              <div className="rounded-[24px] bg-rose-50 border border-rose-100 p-5 mb-4">
                <div className="text-sm text-rose-500 mb-2">오늘의 한 줄</div>
                <textarea
                  value={todayFocus}
                  onChange={(e) => setTodayFocus(e.target.value)}
                  className="w-full min-h-[100px] resize-none rounded-2xl border border-rose-100 bg-white px-4 py-3 outline-none focus:ring-2 focus:ring-rose-200 text-slate-700"
                />
              </div>

              <div>
                <div className="text-base font-semibold mb-3">오늘 꼭 할 일</div>
                <div className="space-y-3">
                  {mustDo.map((item, idx) => (
                    <div key={idx} className="flex items-center gap-3 rounded-2xl bg-white border border-rose-100 px-4 py-3">
                      <input type="checkbox" className="h-4 w-4 accent-pink-400" />
                      <span className="text-slate-700">{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            </SectionCard>

            <SectionCard title="주간 루틴" subtitle="반복되는 일상을 내 리듬에 맞게 정리합니다.">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {weeklyRoutine.map((row) => (
                  <div key={row.day} className="rounded-[24px] bg-pink-50 border border-pink-100 p-4">
                    <div className="font-semibold text-pink-600 mb-3">{row.day}</div>
                    <div className="space-y-2">
                      {row.items.map((item) => (
                        <div key={item} className="rounded-xl bg-white px-3 py-2 text-sm text-slate-700 border border-pink-100">
                          {item}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </SectionCard>
          </div>

          <div className="space-y-6">
            <SectionCard title="오늘의 루틴" subtitle="작은 실천을 가볍게 체크합니다.">
              <div className="space-y-3">
                {[
                  ["morning", "아침 정리하기"],
                  ["reading", "독서 시간 갖기"],
                  ["walk", "산책하기"],
                  ["coffee", "커피 한 잔의 여유"],
                  ["writing", "짧게라도 기록하기"],
                ].map(([key, label]) => (
                  <button
                    key={key}
                    onClick={() => toggle(key)}
                    className={`w-full flex items-center justify-between rounded-2xl px-4 py-4 border transition ${
                      routineChecks[key]
                        ? "bg-pink-100 border-pink-200"
                        : "bg-white border-pink-100 hover:bg-pink-50"
                    }`}
                  >
                    <span className="text-slate-700">{label}</span>
                    <span className={`text-sm px-3 py-1 rounded-full ${routineChecks[key] ? "bg-white text-pink-500" : "bg-pink-50 text-slate-400"}`}>
                      {routineChecks[key] ? "완료" : "대기"}
                    </span>
                  </button>
                ))}
              </div>
            </SectionCard>

            <SectionCard title="돌아보기" subtitle="하루를 무겁지 않게 정리합니다.">
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-slate-500 mb-2">좋았던 점</div>
                  <textarea className="w-full min-h-[90px] resize-none rounded-2xl border border-pink-100 bg-pink-50 px-4 py-3 outline-none focus:ring-2 focus:ring-pink-200" placeholder="오늘 괜찮았던 순간을 짧게 적어봅니다." />
                </div>
                <div>
                  <div className="text-sm text-slate-500 mb-2">조금 아쉬운 점</div>
                  <textarea className="w-full min-h-[90px] resize-none rounded-2xl border border-pink-100 bg-white px-4 py-3 outline-none focus:ring-2 focus:ring-pink-200" placeholder="내일은 조금 다르게 해보고 싶은 것을 적습니다." />
                </div>
              </div>
            </SectionCard>
          </div>
        </div>
      </div>
    </div>
  );
}
