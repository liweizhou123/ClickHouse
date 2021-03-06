import hashlib
import json
import logging
import os
import shutil
import subprocess

import bs4
import closure
import cssmin
import htmlmin
import jinja2
import jsmin

import mdx_clickhouse


def adjust_markdown_html(content):
    soup = bs4.BeautifulSoup(
        content,
        features='html.parser'
    )
    for details in soup.find_all('details'):
        for summary in details.find_all('summary'):
            if summary.parent != details:
                summary.extract()
                details.insert(0, summary)
    for div in soup.find_all('div'):
        div.attrs['role'] = 'alert'
        div_class = div.attrs.get('class')
        for a in div.find_all('a'):
            a_class = a.attrs.get('class')
            if a_class:
                a.attrs['class'] = a_class + ['alert-link']
            else:
                a.attrs['class'] = 'alert-link'
        for p in div.find_all('p'):
            p_class = p.attrs.get('class')
            if p_class and ('admonition-title' in p_class):
                p.attrs['class'] = p_class + ['alert-heading', 'display-5', 'mb-2']
        if div_class and 'admonition' in div.attrs.get('class'):
            if ('info' in div_class) or ('note' in div_class):
                mode = 'alert-primary'
            elif ('attention' in div_class) or ('warning' in div_class):
                mode = 'alert-warning'
            elif 'important' in div_class:
                mode = 'alert-danger'
            elif 'tip' in div_class:
                mode = 'alert-info'
            else:
                mode = 'alert-secondary'
            div.attrs['class'] = div_class + ['alert', 'lead', 'pb-0', 'mb-4', mode]

    return str(soup)


def minify_html(content):
    return htmlmin.minify(content,
                          remove_comments=False,
                          remove_empty_space=True,
                          remove_all_empty_space=False,
                          reduce_empty_attributes=True,
                          reduce_boolean_attributes=False,
                          remove_optional_attribute_quotes=True,
                          convert_charrefs=False,
                          keep_pre=True)


def build_website(args):
    logging.info('Building website')
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader([
            args.website_dir,
            os.path.join(args.docs_dir, '_includes')
        ]),
        extensions=[
            'jinja2.ext.i18n',
            'jinja2_highlight.HighlightExtension'
        ]
    )
    env.extend(jinja2_highlight_cssclass='syntax p-3 my-3')
    translations_dir = os.path.join(args.website_dir, 'locale')
    env.install_gettext_translations(
        mdx_clickhouse.get_translations(translations_dir, 'en'),
        newstyle=True
    )

    shutil.copytree(
        args.website_dir,
        args.output_dir,
        ignore=shutil.ignore_patterns(
            '*.md',
            '*.sh',
            '*.css',
            '*.json',
            'js/*.js',
            'build',
            'docs',
            'public',
            'node_modules',
            'templates',
            'feathericons',
            'locale'
        )
    )

    for root, _, filenames in os.walk(args.output_dir):
        for filename in filenames:
            if filename == 'main.html':
                continue

            path = os.path.join(root, filename)
            if not filename.endswith('.html'):
                continue
            logging.info('Processing %s', path)
            with open(path, 'rb') as f:
                content = f.read().decode('utf-8')

            template = env.from_string(content)
            content = template.render(args.__dict__)

            with open(path, 'wb') as f:
                f.write(content.encode('utf-8'))


def get_css_in(args):
    return [
        f"'{args.website_dir}/css/bootstrap.css'",
        f"'{args.website_dir}/css/docsearch.css'",
        f"'{args.website_dir}/css/base.css'",
        f"'{args.website_dir}/css/docs.css'",
        f"'{args.website_dir}/css/highlight.css'"
    ]


def get_js_in(args):
    return [
        f"'{args.website_dir}/js/jquery.js'",
        f"'{args.website_dir}/js/popper.js'",
        f"'{args.website_dir}/js/bootstrap.js'",
        f"'{args.website_dir}/js/base.js'",
        f"'{args.website_dir}/js/index.js'",
        f"'{args.website_dir}/js/docsearch.js'",
        f"'{args.website_dir}/js/docs.js'"
    ]


def minify_website(args):
    css_in = ' '.join(get_css_in(args))
    css_out = f'{args.output_dir}/css/base.css'
    if args.minify:
        command = f"purifycss -w '*algolia*' --min {css_in} '{args.output_dir}/*.html' " \
            f"'{args.output_dir}/docs/en/**/*.html' '{args.website_dir}/js/**/*.js' > {css_out}"
    else:
        command = f'cat {css_in} > {css_out}'
    logging.info(command)
    output = subprocess.check_output(command, shell=True)
    logging.debug(output)
    with open(css_out, 'rb') as f:
        css_digest = hashlib.sha3_224(f.read()).hexdigest()[0:8]

    js_in = get_js_in(args)
    js_out = f'{args.output_dir}/js/base.js'
    if args.minify:
        js_in = [js[1:-1] for js in js_in]
        closure_args = [
            '--js', *js_in, '--js_output_file', js_out,
            '--compilation_level', 'SIMPLE',
            '--dependency_mode', 'NONE',
            '--third_party', '--use_types_for_optimization',
            '--isolation_mode', 'IIFE'
        ]
        logging.info(closure_args)
        if closure.run(*closure_args):
            raise RuntimeError('failed to run closure compiler')
        with open(js_out, 'r') as f:
            js_content = jsmin.jsmin(f.read())
        with open(js_out, 'w') as f:
            f.write(js_content)

    else:
        js_in = ' '.join(js_in)
        command = f'cat {js_in} > {js_out}'
        logging.info(command)
        output = subprocess.check_output(command, shell=True)
        logging.debug(output)
    with open(js_out, 'rb') as f:
        js_digest = hashlib.sha3_224(f.read()).hexdigest()[0:8]
        logging.info(js_digest)

    if args.minify:
        logging.info('Minifying website')
        for root, _, filenames in os.walk(args.output_dir):
            for filename in filenames:
                path = os.path.join(root, filename)
                if not (
                    filename.endswith('.html') or
                    filename.endswith('.css')
                ):
                    continue

                logging.info('Minifying %s', path)
                with open(path, 'rb') as f:
                    content = f.read().decode('utf-8')
                if filename.endswith('.html'):
                    content = minify_html(content)
                    content = content.replace('base.css?css_digest', f'base.css?{css_digest}')
                    content = content.replace('base.js?js_digest', f'base.js?{js_digest}')
                elif filename.endswith('.css'):
                    content = cssmin.cssmin(content)
                elif filename.endswith('.js'):
                    content = jsmin.jsmin(content)
                with open(path, 'wb') as f:
                    f.write(content.encode('utf-8'))


def process_benchmark_results(args):
    benchmark_root = os.path.join(args.website_dir, 'benchmark')
    for benchmark_kind in ['dbms', 'hardware']:
        results = []
        results_root = os.path.join(benchmark_root, benchmark_kind, 'results')
        for result in sorted(os.listdir(results_root)):
            result_file = os.path.join(results_root, result)
            logging.debug(f'Reading benchmark result from {result_file}')
            with open(result_file, 'r') as f:
                results += json.loads(f.read())
        results_js = os.path.join(args.output_dir, 'benchmark', benchmark_kind, 'results.js')
        with open(results_js, 'w') as f:
            data = json.dumps(results)
            f.write(f'var results = {data};')
