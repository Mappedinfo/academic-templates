#!/usr/bin/env python3
"""按现有 CSV 的分组列汇总一个数值列；输入永不改写。"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--group', required=True)
    parser.add_argument('--value', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--missing-token', action='append', default=[], help='数值列的缺失符号，可重复；空字符串始终视为缺失')
    parser.add_argument('--chunk-size', type=int, default=100000)
    args = parser.parse_args()
    if args.group == args.value or args.chunk_size <= 0:
        parser.error('group/value 必须不同且 chunk-size 为正整数')
    if not args.input.is_file():
        parser.error('输入文件不存在')
    if args.output.exists() or args.output.resolve() == args.input.resolve():
        parser.error('输出已存在或与输入相同；请选择新文件')
    chunks = pd.read_csv(args.input, usecols=[args.group, args.value],
                         dtype={args.group: 'string'}, keep_default_na=False,
                         na_values={args.value: ['', *args.missing_token]}, chunksize=args.chunk_size)
    parts = []
    for chunk in chunks:
        value = pd.to_numeric(chunk[args.value], errors='raise')
        if not value.dropna().map(lambda x: pd.notna(x) and abs(x) != float('inf')).all():
            raise ValueError('数值列包含非有限值')
        frame = pd.DataFrame({args.group: chunk[args.group], '_value': value,
                              '_zero': value.eq(0).fillna(False).astype(int)})
        parts.append(frame.groupby(args.group, dropna=False, observed=True).agg(
            rows=('_value', 'size'), valid=('_value', 'count'), total=('_value', 'sum'), zeros=('_zero', 'sum')).reset_index())
    if not parts:
        raise ValueError('输入没有可汇总的记录')
    combined = pd.concat(parts, ignore_index=True).groupby(args.group, dropna=False, observed=True).agg(
        rows=('rows', 'sum'), valid=('valid', 'sum'), total=('total', 'sum'), zeros=('zeros', 'sum')).reset_index()
    combined['missing'] = combined['rows'] - combined['valid']
    combined['mean'] = (combined['total'] / combined['valid'].where(combined['valid'] > 0))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='') as output:
        combined.to_csv(output, index=False)
    print(f'已保存 {len(combined)} 个组的绘图数据：{args.output}')

if __name__ == '__main__':
    main()
